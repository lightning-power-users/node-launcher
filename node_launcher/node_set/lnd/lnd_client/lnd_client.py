import codecs
import os
from typing import List

# noinspection PyPackageRequirements
import grpc
# noinspection PyProtectedMember,PyPackageRequirements
from google.protobuf.json_format import MessageToDict
# noinspection PyProtectedMember
from google.rpc.code_pb2 import UNAVAILABLE
from grpc._channel import _Rendezvous
from grpc._plugin_wrapping import (_AuthMetadataContext,
                                   _AuthMetadataPluginCallback)

from node_launcher.constants import LND_DIR_PATH, OPERATING_SYSTEM
from node_launcher.logging import log
from . import rpc_pb2 as ln
from . import rpc_pb2_grpc as lnrpc

os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'


class DefaultModel(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)


class PendingChannels(DefaultModel):
    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return None


class LndBalances(object):
    # Ordered by liquidity
    active_off_chain_balance: int = 0
    pending_htlc_balance: int = 0
    confirmed_on_chain_balance: int = 0
    timelocked_on_chain_balance: int = 0
    unconfirmed_off_chain_balance: int = 0
    unconfirmed_on_chain_balance: int = 0
    inactive_off_chain_balance: int = 0
    reserve_off_chain_balance: int = 0

    def total_offchain(self):
        return (
            self.active_off_chain_balance
            + self.pending_htlc_balance
            + self.unconfirmed_off_chain_balance
            + self.inactive_off_chain_balance
        )

    def total_onchain(self):
        return (
            self.confirmed_on_chain_balance
            + self.timelocked_on_chain_balance
            + self.unconfirmed_on_chain_balance
        )

    def total_balance(self):
        return (
            self.active_off_chain_balance
            + self.pending_htlc_balance
            + self.confirmed_on_chain_balance
            + self.timelocked_on_chain_balance
            + self.unconfirmed_off_chain_balance
            + self.unconfirmed_on_chain_balance
            + self.inactive_off_chain_balance
        )

    def __repr__(self):
        return f'Total: {self.total_balance()} \n' \
               f'Reserve: {self.reserve_off_chain_balance} \n' \
               f'Offchain: {self.total_offchain()} \n' \
               f'Onchain: {self.total_onchain()} \n'


class LndClient(object):
    def __init__(self, lnd_configuration=None,
                 lnddir: str = LND_DIR_PATH[OPERATING_SYSTEM],
                 grpc_port: int = None, grpc_host: str = None,
                 macaroon_path: str = None):
        self.lnd_configuration = lnd_configuration
        self._lnddir = lnddir
        self._grpc_port = grpc_port
        self._grpc_host = grpc_host
        if macaroon_path is not None:
            self._macaroon_path = macaroon_path
        else:
            self._macaroon_path = lnddir
        self._lnd_client = None
        self._wallet_unlocker = None

        self.grpc_options = [
            ('grpc.max_receive_message_length', 33554432),
            ('grpc.max_send_message_length', 33554432),
        ]

    def reset(self):
        self._lnd_client = None
        self._wallet_unlocker = None

    @property
    def lnd_client(self):
        if self._lnd_client is not None:
            return self._lnd_client
        auth_credentials = grpc.metadata_call_credentials(
            self.metadata_callback)

        credentials = grpc.composite_channel_credentials(
            self.get_cert_credentials(),
            auth_credentials)

        grpc_channel = grpc.secure_channel(
            f'{self.grpc_host}:{self.grpc_port}',
            credentials,
            options=self.grpc_options
        )
        self._lnd_client = lnrpc.LightningStub(grpc_channel)
        return self._lnd_client

    @property
    def wallet_unlocker(self):
        if self._wallet_unlocker is not None:
            return self._wallet_unlocker

        grpc_channel = grpc.secure_channel(
            f'{self.grpc_host}:{self.grpc_port}',
            credentials=self.get_cert_credentials()
        )
        self._wallet_unlocker = lnrpc.WalletUnlockerStub(grpc_channel)
        return self._wallet_unlocker

    @property
    def lnddir(self) -> str:
        if self.lnd_configuration is not None:
            return self.lnd_configuration.lnddir
        else:
            return self._lnddir

    @property
    def grpc_port(self) -> int:
        if self.lnd_configuration is not None:
            return self.lnd_configuration.grpc_port
        else:
            return self._grpc_port

    @property
    def grpc_host(self) -> str:
        if self.lnd_configuration is not None:
            return 'localhost'
        else:
            return self._grpc_host

    @property
    def macaroon_path(self) -> str:
        if self.lnd_configuration is not None:
            return self.lnd_configuration.macaroon_path
        else:
            return self._macaroon_path

    @property
    def tls_cert_path(self) -> str:
        return os.path.join(self.lnddir, 'tls.cert')

    @property
    def tls_key_path(self) -> str:
        return os.path.join(self.lnddir, 'tls.key')

    def get_cert_credentials(self):
        lnd_tls_cert = open(self.tls_cert_path, 'rb').read()
        cert_credentials = grpc.ssl_channel_credentials(lnd_tls_cert)
        return cert_credentials

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

    def generate_seed(self, seed_password: str = None) -> ln.GenSeedResponse:
        request = ln.GenSeedRequest()
        if seed_password is not None:
            request.aezeed_passphrase = seed_password.encode('latin1')
        response = self.wallet_unlocker.GenSeed(request)
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
        response = self.wallet_unlocker.InitWallet(request)
        return response

    def unlock(self, wallet_password: str) -> ln.UnlockWalletResponse:
        request = ln.UnlockWalletRequest()
        request.wallet_password = wallet_password.encode('latin1')
        response = self.wallet_unlocker.UnlockWallet(request)
        return response

    def get_info(self) -> ln.GetInfoResponse:
        request = ln.GetInfoRequest()
        response = self.lnd_client.GetInfo(request)
        return response

    def get_node_info(self, pub_key: str) -> ln.NodeInfo:
        request = ln.NodeInfoRequest()
        request.pub_key = pub_key
        response = self.lnd_client.GetNodeInfo(request)
        return response

    def get_chan_info(self, chan_id: int) -> ln.ChannelEdge:
        request = ln.ChanInfoRequest()
        request.chan_id = int(chan_id)
        response = self.lnd_client.GetChanInfo(request)
        return response

    def connect_peer(self, pubkey: str, host: str,
                     timeout: int = 3) -> ln.ConnectPeerResponse:
        address = ln.LightningAddress(pubkey=pubkey, host=host)
        request = ln.ConnectPeerRequest(addr=address)
        response = self.lnd_client.ConnectPeer(request, timeout=timeout)
        return response

    def channel_balance(self) -> ln.ChannelBalanceResponse:
        request = ln.ChannelBalanceRequest()
        response = self.lnd_client.ChannelBalance(request)
        return response

    def wallet_balance(self) -> ln.WalletBalanceResponse:
        request = ln.WalletBalanceRequest()
        response = self.lnd_client.WalletBalance(request)
        return response

    def list_unspent(self) -> ln.ListUnspentResponse:
        request = ln.ListUnspentRequest(min_confs=0, max_confs=10000000)
        response = self.lnd_client.ListUnspent(request)
        return response

    def get_lnd_balances(self) -> LndBalances:
        log.debug('get_lnd_balances')
        b = LndBalances()

        open_channels = self.list_channels()
        log.debug('open_channels', count=len(open_channels))
        for oc in open_channels:
            if oc.active:
                b.active_off_chain_balance += oc.local_balance
            else:
                b.inactive_off_chain_balance += oc.local_balance
            b.reserve_off_chain_balance += oc.local_chan_reserve_sat
            b.pending_htlc_balance += oc.unsettled_balance

        channel_balance = self.channel_balance()
        log.debug('channel_balance', channel_balance=channel_balance)
        log.debug('calculated',
                  active_off_chain_balance=b.active_off_chain_balance,
                  inactive_off_chain_balance=b.inactive_off_chain_balance,
                  total_off_chain_balance=b.active_off_chain_balance+b.inactive_off_chain_balance,
                  reserve_off_chain_balance=b.reserve_off_chain_balance,
                  pending_htlc_balance=b.pending_htlc_balance,
                  )
        assert b.active_off_chain_balance + b.inactive_off_chain_balance == channel_balance.balance

        pending_channels = self.pending_channels()
        for pc in pending_channels.pending_open_channels:
            b.unconfirmed_off_chain_balance += pc.channel.local_balance
            b.reserve_off_chain_balance += pc.channel.local_chan_reserve_sat
        for pc in pending_channels.waiting_close_channels:
            b.unconfirmed_on_chain_balance += pc.channel.local_balance
        for pc in pending_channels.pending_force_closing_channels:
            b.timelocked_on_chain_balance += pc.limbo_balance

        log.debug('calculated',
                  unconfirmed_off_chain_balance=b.unconfirmed_off_chain_balance)
        assert b.timelocked_on_chain_balance == pending_channels.total_limbo_balance
        assert b.unconfirmed_off_chain_balance == channel_balance.pending_open_balance

        wallet_balance = self.wallet_balance()
        b.confirmed_on_chain_balance = wallet_balance.confirmed_balance
        log.debug('wallet_balance',
                  confirmed_balance=wallet_balance.confirmed_balance,
                  unconfirmed_balance=wallet_balance.unconfirmed_balance)
        log.debug('calculated',
                  unconfirmed_on_chain_balance=b.unconfirmed_on_chain_balance,
                  timelocked_on_chain_balance=b.timelocked_on_chain_balance,
                  total_unspendable_on_chain_balance=b.unconfirmed_on_chain_balance+b.timelocked_on_chain_balance)

        utxos = self.list_unspent().utxos
        total_on_chain = 0
        for utxo in utxos:
            total_on_chain += utxo.amount_sat

        log.debug('utxo calculated', total_on_chain=total_on_chain)
        log.debug('channel and balance calculated',
                  total=b.unconfirmed_on_chain_balance + b.confirmed_on_chain_balance,
                  unconfirmed=b.unconfirmed_on_chain_balance,
                  confirmed=b.confirmed_on_chain_balance)
        assert total_on_chain == b.unconfirmed_on_chain_balance + b.confirmed_on_chain_balance

        return b

    def list_all(self):
        return {
            'peers': self.list_peers(),
            'open_channels': self.list_channels(),
            'pending_channels': self.list_pending_channels(),
            'closed_channels': self.closed_channels()
        }

    def list_peers(self) -> List[ln.Peer]:
        request = ln.ListPeersRequest()
        response = self.lnd_client.ListPeers(request)
        return response.peers

    def list_channels(self) -> List[ln.Channel]:
        request = ln.ListChannelsRequest()
        request.active_only = False
        request.inactive_only = False
        request.public_only = False
        request.private_only = False
        response = self.lnd_client.ListChannels(request)
        return response.channels

    def pending_channels(self) -> ln.PendingChannelsResponse:
        request = ln.PendingChannelsRequest()
        response = self.lnd_client.PendingChannels(request)
        return response

    def list_pending_channels(self) -> List[PendingChannels]:
        response = self.pending_channels()
        pending_channels = []
        pending_types = [
            'pending_open_channels',
            # 'pending_closing_channels', DEPRECATED
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
        kwargs['node_pubkey'] = codecs.decode(kwargs['node_pubkey_string'],
                                              'hex')
        request = ln.OpenChannelRequest(**kwargs)
        log.debug('open_channel', request=MessageToDict(request))
        response = self.lnd_client.OpenChannel(request)
        return response

    def create_invoice(self, **kwargs) -> ln.AddInvoiceResponse:
        request = ln.Invoice(**kwargs)
        response = self.lnd_client.AddInvoice(request)
        return response

    def get_new_address(self, address_type: str = 'NESTED_PUBKEY_HASH') -> str:
        request = ln.NewAddressRequest(type=address_type)
        response = self.lnd_client.NewAddress(request)
        return response.address

    def get_graph(self) -> ln.ChannelGraph:
        request = ln.ChannelGraphRequest()
        request.include_unannounced = True
        log.debug('get_graph', request=MessageToDict(request))
        response = self.lnd_client.DescribeGraph(request)
        return response

    def close_channel(self, channel_point: str, force: bool, sat_per_byte: int):
        request = ln.CloseChannelRequest()
        request.channel_point = channel_point
        request.force = force
        request.sat_per_byte = sat_per_byte
        response = self.lnd_client.CloseChannel(request)
        return response

    def closed_channels(self):
        request = ln.ClosedChannelsRequest()
        response = self.lnd_client.ClosedChannels(request)
        return response.channels

    def stop(self):
        request = ln.StopRequest()
        try:
            response = self.lnd_client.StopDaemon(request)
            log.debug('lnd stop response', response=response)
        except _Rendezvous:
            log.error('stop lnd error', exc_info=True)
            raise

    def debug_level(self, show: bool = None, level_spec: str = None):
        request = ln.DebugLevelRequest()
        if show is not None:
            request.show = show
        if level_spec is not None:
            request.level_spec = level_spec
        response = self.lnd_client.DebugLevel(request)
        return response
