from typing import List
import base64
import os
import socket
import ssl

from PySide2.QtCore import QProcess
import qrcode

from node_launcher.constants import (
    IS_WINDOWS,
    LND_DEFAULT_GRPC_PORT,
    LND_DEFAULT_PEER_PORT,
    LND_DEFAULT_REST_PORT,
    LND_DIR_PATH,
    OPERATING_SYSTEM
)
from node_launcher.node_set.bitcoin import Bitcoin
from node_launcher.services.configuration_file import ConfigurationFile
from node_launcher.services.lnd_software import LndSoftware
from node_launcher.utilities.utilities import get_port


class Lnd(object):
    bitcoin: Bitcoin
    file: ConfigurationFile
    software: LndSoftware
    process: QProcess

    def __init__(self, configuration_file_path: str, bitcoin: Bitcoin):
        self.running = False
        self.is_unlocked = False
        self.bitcoin = bitcoin
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
        self.file['bitcoind.rpchost'] = f'127.0.0.1:{self.bitcoin.rpc_port}'
        self.file['bitcoind.rpcuser'] = self.bitcoin.file['rpcuser']
        self.file['bitcoind.rpcpass'] = self.bitcoin.file['rpcpassword']
        self.file['bitcoind.zmqpubrawblock'] = self.bitcoin.file[
            'zmqpubrawblock']
        self.file['bitcoind.zmqpubrawtx'] = self.bitcoin.file['zmqpubrawtx']

        if self.file['restlisten'] is None:
            if self.bitcoin.file['testnet']:
                self.rest_port = get_port(LND_DEFAULT_REST_PORT + 1)
            else:
                self.rest_port = get_port(LND_DEFAULT_REST_PORT)
            self.file['restlisten'] = f'127.0.0.1:{self.rest_port}'
        else:
            self.rest_port = self.file['restlisten'].split(':')[-1]

        if not self.file['rpclisten']:
            if self.bitcoin.file['testnet']:
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

        self.macaroon_path = os.path.join(
            self.lnddir,
            'data',
            'chain',
            'bitcoin',
            str(self.bitcoin.network)
        )
        self.config_snapshot = self.file.snapshot.copy()
        self.file.file_watcher.fileChanged.connect(self.config_file_changed)
        self.bitcoin.file.file_watcher.fileChanged.connect(
            self.bitcoin_config_file_changed)

        self.process = QProcess()
        self.process.setProgram(self.software.lnd)
        self.process.setCurrentReadChannel(0)
        self.process.setArguments(self.args)
        self.process.start()

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

        if self.bitcoin.file['testnet']:
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
            if self.bitcoin.file['testnet']:
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
        if self.bitcoin.file['testnet']:
            args.append(f'--network={self.bitcoin.network}')
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
        self.file['bitcoind.rpchost'] = f'127.0.0.1:{self.bitcoin.rpc_port}'
        self.file['bitcoind.rpcuser'] = self.bitcoin.file['rpcuser']
        self.file['bitcoind.rpcpass'] = self.bitcoin.file['rpcpassword']
        self.file['bitcoind.zmqpubrawblock'] = self.bitcoin.file[
            'zmqpubrawblock']
        self.file['bitcoind.zmqpubrawtx'] = self.bitcoin.file['zmqpubrawtx']

    @property
    def restart_required(self):
        if self.running:
            # Did bitcoin details change
            if self.bitcoin.restart_required:
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
    def lndconnect_url(self):
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
    def lndconnect_qrcode(self):
        img = qrcode.make(self.lndconnect_url)
        return img
