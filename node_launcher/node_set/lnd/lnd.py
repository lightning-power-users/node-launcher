from typing import List
import base64
import os
import socket
import ssl

# noinspection PyProtectedMember
from grpc._channel import _Rendezvous
from PySide2.QtCore import QThreadPool
import qrcode

from node_launcher.constants import (
    IS_WINDOWS,
    LND_DEFAULT_GRPC_PORT,
    LND_DEFAULT_PEER_PORT,
    LND_DEFAULT_REST_PORT,
    LND_DIR_PATH,
    OPERATING_SYSTEM,
    keyring)
from node_launcher.gui.components.thread_worker import Worker
from node_launcher.logging import log
from node_launcher.node_set.bitcoind.bitcoind_node import BitcoindNode
from node_launcher.node_set.lib.configuration_file import ConfigurationFile
from node_launcher.node_set.lib.get_random_password import get_random_password
from node_launcher.port_utilities import get_port
from .lnd_client import LndClient
from .lnd_process import LndProcess
from .lnd_software import LndSoftware


class Lnd(object):
    bitcoind_node: BitcoindNode
    client: LndClient
    file: ConfigurationFile
    software: LndSoftware
    process: LndProcess

    def __init__(self, bitcoind_node: BitcoindNode, configuration_file_path: str = None):
        self.running = False
        self.is_unlocked = False
        self.bitcoind_node = bitcoind_node
        if configuration_file_path is None:
            file_name = 'lnd.conf'
            lnd_dir_path = LND_DIR_PATH[OPERATING_SYSTEM]
            configuration_file_path = os.path.join(lnd_dir_path, file_name)
            log.info(
                'lnd configuration_file_path',
                configuration_file_path=configuration_file_path
            )

        self.file = ConfigurationFile(configuration_file_path)
        self.software = LndSoftware()

        self.lnddir = LND_DIR_PATH[OPERATING_SYSTEM]

        # Previous versions of the launcher set lnddir in the config file,
        # but it is not a valid key so this helps old users upgrading
        if self.file['lnddir'] is not None:
            self.file['lnddir'] = None

        if self.file['debuglevel'] is None:
            self.file['debuglevel'] = 'info'

        self.file['bitcoin.active'] = True
        self.file['bitcoin.node'] = 'bitcoind'
        self.file['bitcoind.rpchost'] = f'127.0.0.1:{self.bitcoind_node.rpc_port}'
        self.file['bitcoind.rpcuser'] = self.bitcoind_node.file['rpcuser']
        self.file['bitcoind.rpcpass'] = self.bitcoind_node.file['rpcpassword']
        self.file['bitcoind.zmqpubrawblock'] = self.bitcoind_node.file[
            'zmqpubrawblock']
        self.file['bitcoind.zmqpubrawtx'] = self.bitcoind_node.file['zmqpubrawtx']

        if self.file['restlisten'] is None:
            if self.bitcoind_node.file['testnet']:
                self.rest_port = get_port(LND_DEFAULT_REST_PORT + 1)
            else:
                self.rest_port = get_port(LND_DEFAULT_REST_PORT)
            self.file['restlisten'] = f'127.0.0.1:{self.rest_port}'
        else:
            self.rest_port = self.file['restlisten'].split(':')[-1]

        if not self.file['rpclisten']:
            if self.bitcoind_node.file['testnet']:
                self.grpc_port = get_port(LND_DEFAULT_GRPC_PORT + 1)
            else:
                self.grpc_port = get_port(LND_DEFAULT_GRPC_PORT)
            self.file['rpclisten'] = f'127.0.0.1:{self.grpc_port}'
        else:
            self.grpc_port = int(self.file['rpclisten'].split(':')[-1])

        if not self.file['tlsextraip']:
            self.file['tlsextraip'] = '127.0.0.1'

        if self.file['color'] is None:
            self.file['color'] = '#000000'

        self.file['listen'] = 'localhost'
        self.file['tor.active'] = True
        self.file['tor.v3'] = True
        self.file['tor.streamisolation'] = True

        self.macaroon_path = os.path.join(
            self.lnddir,
            'data',
            'chain',
            'bitcoin',
            str(self.bitcoind_node.network)
        )
        self.config_snapshot = self.file.snapshot.copy()
        self.file.file_watcher.fileChanged.connect(self.config_file_changed)
        self.bitcoind_node.file.file_watcher.fileChanged.connect(
            self.bitcoin_config_file_changed)

        self.client = LndClient(self)

        self.threadpool = QThreadPool()

        self.process = LndProcess(self.software.lnd, self.args)
        self.software.ready.connect(self.process.start)
        self.process.ready_to_unlock.connect(self.auto_unlock_wallet)

    @property
    def args(self):
        if IS_WINDOWS:
            arg_list = [
                f'--configfile={self.file.path}',
            ]
        else:
            arg_list = [
                f'--configfile="{self.file.path}"',
            ]

        if self.bitcoind_node.file['testnet']:
            arg_list += [
                '--bitcoin.testnet'
            ]
        else:
            arg_list += [
                '--bitcoin.mainnet'
            ]
        return arg_list

    @property
    def node_port(self) -> str:
        if self.file['listen'] is None:
            if self.bitcoind_node.file['testnet']:
                port = get_port(LND_DEFAULT_PEER_PORT + 1)
            else:
                port = get_port(LND_DEFAULT_PEER_PORT)
            self.file['listen'] = f'127.0.0.1:{port}'
        else:
            if not isinstance(self.file['listen'], list):
                port = self.file['listen'].split(':')[-1]
            else:
                port = self.file['listen'][0].split(':')[-1]
        return port

    def test_tls_cert(self):
        context = ssl.create_default_context()
        context.load_verify_locations(cafile=self.tls_cert_path)
        conn = context.wrap_socket(socket.socket(socket.AF_INET),
                                   server_hostname='127.0.0.1')
        conn.connect(('127.0.0.1', int(self.rest_port)))
        cert = conn.getpeercert()
        return cert

    @property
    def admin_macaroon_path(self) -> str:
        path = os.path.join(self.macaroon_path, 'admin.macaroon')
        return path

    @property
    def wallet_path(self) -> str:
        wallet_path = os.path.join(self.macaroon_path, 'wallet.db')
        return wallet_path

    @property
    def has_wallet(self) -> bool:
        return os.path.isfile(self.wallet_path)

    @property
    def tls_cert_path(self) -> str:
        tls_cert_path = os.path.join(self.lnddir, 'tls.cert')
        return tls_cert_path

    def lncli_arguments(self) -> List[str]:
        args = []
        if self.grpc_port != LND_DEFAULT_GRPC_PORT:
            args.append(f'--rpcserver=127.0.0.1:{self.grpc_port}')
        if self.bitcoind_node.file['testnet']:
            args.append(f'--network={self.bitcoind_node.network}')
        if self.lnddir != LND_DIR_PATH[OPERATING_SYSTEM]:
            args.append(f'''--lnddir="{self.lnddir}"''')
            args.append(f'--macaroonpath="{self.macaroon_path}"')
            args.append(f'--tlscertpath="{self.tls_cert_path}"')
        return args

    @property
    def lncli(self) -> str:
        base_command = [
            f'"{self.software.lncli}"',
        ]
        base_command += self.lncli_arguments()
        return ' '.join(base_command)

    @property
    def rest_url(self) -> str:
        return f'https://127.0.0.1:{self.rest_port}'

    @property
    def grpc_url(self) -> str:
        return f'127.0.0.1:{self.grpc_port}'

    def config_file_changed(self):
        # Refresh config file
        self.file.file_watcher.blockSignals(True)
        self.file.populate_cache()
        self.file.file_watcher.blockSignals(False)
        if self.file['restlisten']:
            self.rest_port = int(self.file['restlisten'].split(':')[-1])
        if self.file['rpclisten']:
            self.grpc_port = int(self.file['rpclisten'].split(':')[-1])

        # Some text editors do not modify the file, they delete and replace the file
        # Check if file is still in file_watcher list of files, if not add back
        files_watched = self.file.file_watcher.files()
        if len(files_watched) == 0:
            self.file.file_watcher.addPath(self.file.path)

    def bitcoin_config_file_changed(self):
        # Refresh config file
        self.file.file_watcher.blockSignals(True)
        self.file.populate_cache()
        self.file.file_watcher.blockSignals(False)
        self.file['bitcoind.rpchost'] = f'127.0.0.1:{self.bitcoind_node.rpc_port}'
        self.file['bitcoind.rpcuser'] = self.bitcoind_node.file['rpcuser']
        self.file['bitcoind.rpcpass'] = self.bitcoind_node.file['rpcpassword']
        self.file['bitcoind.zmqpubrawblock'] = self.bitcoind_node.file[
            'zmqpubrawblock']
        self.file['bitcoind.zmqpubrawtx'] = self.bitcoind_node.file['zmqpubrawtx']

    @property
    def restart_required(self):
        if self.running:
            # Did bitcoin details change
            if self.bitcoind_node.restart_required:
                return True and self.running

            old_config = self.config_snapshot.copy()
            new_config = self.file.snapshot

            fields = [
                'restlisten', 'listen', 'rpclisten'
            ]

            for field in fields:
                # First check if field is found in both configs
                found_in_old_config = field in old_config.keys()
                found_in_new_config = field in new_config.keys()
                if found_in_old_config != found_in_new_config:
                    return True

                # Now check that values are the same
                if found_in_old_config:
                    if old_config[field] != new_config[field]:
                        return True

        return False

    @staticmethod
    def base64URL_from_base64(s):
        return s.replace('+', '-').replace('/', '_').rstrip('=')

    @property
    def lndconnect_mobile_url(self):
        host = self.grpc_url.split(':')[0]
        port = self.grpc_url.split(':')[1]
        with open(self.tls_cert_path, 'r') as cert_file:
            lines = cert_file.read().split('\n')
            lines = [line for line in lines if line != '']
            cert = ''.join(lines[1:-1])
            cert = self.base64URL_from_base64(cert)

        with open(self.admin_macaroon_path, 'rb') as macaroon_file:
            macaroon = base64.b64encode(macaroon_file.read()).decode('ascii')
            macaroon = self.base64URL_from_base64(macaroon)

        return f'lndconnect://{host}:{port}?cert={cert}&macaroon={macaroon}'

    @property
    def lndconnect_url(self):
        host = self.grpc_url.split(':')[0]
        port = self.grpc_url.split(':')[1]
        return f'lndconnect://{host}:{port}' \
            f'?cert={self.tls_cert_path}&macaroon={self.admin_macaroon_path}'

    @property
    def lndconnect_qrcode(self):
        img = qrcode.make(self.lndconnect_mobile_url)
        return img

    def reset_tls(self):
        os.remove(self.client.tls_cert_path)
        os.remove(self.client.tls_key_path)
        self.process.terminate()
        self.client.reset()

    def auto_unlock_wallet(self):
        keyring_service_name = f'lnd_mainnet_wallet_password'
        keyring_user_name = self.file['bitcoind.rpcuser']
        log.info(
            'auto_unlock_wallet_get_password',
            keyring_service_name=keyring_service_name,
            keyring_user_name=keyring_user_name
        )
        password = keyring.get_password(
            service=keyring_service_name,
            username=keyring_user_name,
        )
        worker = Worker(
            fn=self.unlock_wallet,
            lnd=self,
            password=password
        )
        worker.signals.result.connect(self.handle_unlock_wallet)
        self.threadpool.start(worker)

    @staticmethod
    def unlock_wallet(lnd, progress_callback, password: str):
        if password is None:
            return 'wallet not found'
        client = LndClient(lnd)
        try:
            client.unlock(password)
            return None
        except _Rendezvous as e:
            details = e.details()
            return details

    def generate_seed(self, new_seed_password: str):
        try:
            generate_seed_response = self.client.generate_seed(
                seed_password=new_seed_password
            )
        except _Rendezvous:
            log.error('generate_seed error', exc_info=True)
            raise

        seed = generate_seed_response.cipher_seed_mnemonic

        keyring_service_name = f'lnd_seed'
        keyring_user_name = ''.join(seed[0:2])
        log.info(
            'generate_seed',
            keyring_service_name=keyring_service_name,
            keyring_user_name=keyring_user_name
        )

        keyring.set_password(
            service=keyring_service_name,
            username=keyring_user_name,
            password=' '.join(seed)
        )

        keyring.set_password(
            service=f'{keyring_service_name}_seed_password',
            username=keyring_user_name,
            password=new_seed_password
        )
        return seed

    def handle_unlock_wallet(self, details: str):
        if details is None:
            return
        details = details.lower()
        # The Wallet Unlocker gRPC service disappears from LND's API
        # after the wallet is unlocked (or created/recovered)
        if 'unknown service lnrpc.walletunlocker' in details:
            pass
        # User needs to create a new wallet
        elif 'wallet not found' in details:
            new_wallet_password = get_random_password()
            keyring_service_name = keyring_user_name = f'lnd_wallet_password'
            log.info(
                'create_wallet',
                keyring_service_name=keyring_service_name,
                keyring_user_name=keyring_user_name
            )
            keyring.set_password(
                service=keyring_service_name,
                username=keyring_user_name,
                password=new_wallet_password
            )
            seed = self.generate_seed(new_wallet_password)
            try:
                self.client.initialize_wallet(
                    wallet_password=new_wallet_password,
                    seed=seed,
                    seed_password=new_wallet_password
                )
            except _Rendezvous:
                log.error('initialize_wallet error', exc_info=True)
                raise
            keyring.set_password(
                service=f'lnd_mainnet_wallet_password',
                username=self.file['bitcoind.rpcuser'],
                password=new_wallet_password
            )
        else:
            log.warning(
                'unlock_wallet failed',
                details=details,
                exc_info=True
            )
