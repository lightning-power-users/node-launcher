import codecs
import os
from typing import List

# noinspection PyPackageRequirements
import grpc
# noinspection PyProtectedMember,PyPackageRequirements
from google.protobuf.json_format import MessageToDict
from grpc._plugin_wrapping import (_AuthMetadataContext,
                                   _AuthMetadataPluginCallback)

from . import rpc_pb2 as ln
from . import rpc_pb2_grpc as lnrpc

from node_launcher.node_set.lnd import Lnd
from website.models import PendingChannels

os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'


class LndClient(object):
    def __init__(self, lnd: Lnd = None, lnddir: str = None,
                 grpc_port: int = None, grpc_host: str = None,
                 macaroon_path: str = None):
        self.lnd = lnd
        self._lnddir = lnddir
        self._grpc_port = grpc_port
        self._grpc_host = grpc_host
        self._macaroon_path = macaroon_path

    @property
    def lnddir(self) -> str:
        if self.lnd is not None:
            return self.lnd.file['lnddir']
        else:
            return self._lnddir

    @property
    def grpc_port(self) -> int:
        if self.lnd is not None:
            return self.lnd.grpc_port
        else:
            return self._grpc_port

    @property
    def grpc_host(self) -> str:
        if self.lnd is not None:
            return 'localhost'
        else:
            return self._grpc_host

    @property
    def macaroon_path(self) -> str:
        if self.lnd is not None:
            return self.lnd.macaroon_path
        else:
            return self._macaroon_path

    @property
    def tls_cert_path(self) -> str:
        return os.path.join(self.lnddir, 'tls.cert')

    def get_cert_credentials(self):
        lnd_tls_cert = open(self.tls_cert_path, 'rb').read()
        cert_credentials = grpc.ssl_channel_credentials(lnd_tls_cert)
        return cert_credentials

    def wallet_unlocker(self):
        grpc_channel = grpc.secure_channel(f'{self.grpc_host}:{self.grpc_port}',
                                           credentials=self.get_cert_credentials())
        return lnrpc.WalletUnlockerStub(grpc_channel)

    # noinspection PyUnusedLocal
    def metadata_callback(self,
                          context: _AuthMetadataPluginCallback,
                          callback: _AuthMetadataContext):
        admin_macaroon_path = os.path.join(self.macaroon_path, 'admin.macaroon')
        with open(admin_macaroon_path, 'rb') as f:
            macaroon_bytes = f.read()
            macaroon = codecs.encode(macaroon_bytes, 'hex')
        # noinspection PyCallingNonCallable
        callback([('macaroon', macaroon)], None)

    def lnd_client(self):
        auth_credentials = grpc.metadata_call_credentials(self.metadata_callback)
        credentials = grpc.composite_channel_credentials(self.get_cert_credentials(),
                                                         auth_credentials)
        grpc_channel = grpc.secure_channel(f'{self.grpc_host}:{self.grpc_port}',
                                           credentials,
                                           )
        return lnrpc.LightningStub(grpc_channel)

    def generate_seed(self, seed_password: str = None) -> ln.GenSeedResponse:
        request = ln.GenSeedRequest()
        if seed_password is not None:
            request.aezeed_passphrase = seed_password.encode('latin1')
        response = self.wallet_unlocker().GenSeed(request)
        return response

    def initialize_wallet(self, wallet_password: str,
                          seed: List[str],
                          seed_password: str = None,
                          recovery_window: int = None) -> ln.InitWalletResponse:
        request = ln.InitWalletRequest()
        request.wallet_password = wallet_password.encode('latin1')
        request.cipher_seed_mnemonic.extend(seed)
        if seed_password is not None:
            request.aezeed_passphrase = seed_password.encode('latin1')
        if recovery_window is not None:
            request.recovery_window = recovery_window
        response = self.wallet_unlocker().InitWallet(request)
        return response

    def unlock(self, wallet_password: str) -> ln.UnlockWalletResponse:
        request = ln.UnlockWalletRequest()
        request.wallet_password = wallet_password.encode('latin1')
        response = self.wallet_unlocker().UnlockWallet(request)
        return response

    def get_info(self) -> ln.GetInfoResponse:
        request = ln.GetInfoRequest()
        response = self.lnd_client().GetInfo(request, timeout=1)
        return response

    def get_node_info(self, pub_key: str) -> ln.NodeInfo:
        request = ln.NodeInfoRequest()
        request.pub_key = pub_key
        response = self.lnd_client().GetNodeInfo(request, timeout=1)
        return response

    def connect_peer(self, pubkey: str, host: str) -> ln.ConnectPeerResponse:
        address = ln.LightningAddress(pubkey=pubkey, host=host)
        request = ln.ConnectPeerRequest(addr=address)
        response = self.lnd_client().ConnectPeer(request, timeout=1)
        return response

    def list_peers(self) -> List[ln.Peer]:
        request = ln.ListPeersRequest()
        response = self.lnd_client().ListPeers(request)
        return response.peers

    def list_channels(self) -> List[ln.Channel]:
        request = ln.ListChannelsRequest()
        response = self.lnd_client().ListChannels(request, timeout=1)
        return response.channels

    def list_pending_channels(self) -> List[PendingChannels]:
        request = ln.PendingChannelsRequest()
        response = self.lnd_client().PendingChannels(request, timeout=1)
        pending_channels = []
        pending_types = [
            'pending_open_channels',
            'pending_closing_channels',
            'pending_force_closing_channels',
            'waiting_close_channels'
        ]
        for pending_type in pending_types:
            for pending_channel in getattr(response, pending_type):
                channel_dict = MessageToDict(pending_channel)
                nested_data = channel_dict.pop('channel')
                # noinspection PyDictCreation
                flat_dict = {**channel_dict, **nested_data}
                flat_dict['pending_type'] = pending_type
                pending_channel_model = PendingChannels(**flat_dict)
                pending_channels.append(pending_channel_model)
        return pending_channels

    def open_channel(self, **kwargs):
        kwargs['node_pubkey'] = codecs.decode(kwargs['node_pubkey_string'], 'hex')
        request = ln.OpenChannelRequest(**kwargs)
        response = self.lnd_client().OpenChannel(request)
        return response

    def create_invoice(self, **kwargs) -> ln.AddInvoiceResponse:
        request = ln.Invoice(**kwargs)
        response = self.lnd_client().AddInvoice(request)
        return response

    def get_new_address(self, address_type: str = 'NESTED_PUBKEY_HASH') -> str:
        request = ln.NewAddressRequest(type=address_type)
        response = self.lnd_client().NewAddress(request)
        return response.address
