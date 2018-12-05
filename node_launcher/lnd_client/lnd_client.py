import codecs
import os
from typing import List

# noinspection PyPackageRequirements
import grpc
# noinspection PyProtectedMember,PyPackageRequirements
from grpc._plugin_wrapping import (_AuthMetadataContext,
                                   _AuthMetadataPluginCallback)

import node_launcher.lnd_client.rpc_pb2 as ln
import node_launcher.lnd_client.rpc_pb2_grpc as lnrpc
from node_launcher.configuration import Configuration

os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'


class LndClient(object):
    def __init__(self, configuration: Configuration):
        self.c = configuration
        lnd_tls_cert_path = os.path.join(self.c.lnd.lnddir, 'tls.cert')
        self.lnd_tls_cert = open(lnd_tls_cert_path, 'rb').read()
        self.cert_credentials = grpc.ssl_channel_credentials(self.lnd_tls_cert)

    def wallet_unlocker(self):
        grpc_channel = grpc.secure_channel(f'localhost:{self.c.lnd.grpc_port}',
                                           credentials=self.cert_credentials)
        return lnrpc.WalletUnlockerStub(grpc_channel)

    # noinspection PyUnusedLocal
    def metadata_callback(self,
                          context: _AuthMetadataPluginCallback,
                          callback: _AuthMetadataContext):
        admin_macaroon_path = os.path.join(self.c.lnd.macaroon_path, 'admin.macaroon')
        with open(admin_macaroon_path, 'rb') as f:
            macaroon_bytes = f.read()
            macaroon = codecs.encode(macaroon_bytes, 'hex')
        # noinspection PyCallingNonCallable
        callback([('macaroon', macaroon)], None)

    def lnd_client(self):
        auth_credentials = grpc.metadata_call_credentials(self.metadata_callback)
        credentials = grpc.composite_channel_credentials(self.cert_credentials,
                                                         auth_credentials)
        grpc_channel = grpc.secure_channel(f'localhost:{self.c.lnd.grpc_port}',
                                           credentials)
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
