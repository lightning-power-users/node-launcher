import base64
import os
import socket
import ssl
from typing import List

import qrcode

from node_launcher.constants import (
    IS_WINDOWS,
    LND_DEFAULT_GRPC_PORT,
    LND_DEFAULT_PEER_PORT,
    LND_DEFAULT_REST_PORT,
    LND_DIR_PATH,
    OPERATING_SYSTEM
)
from node_launcher.logging import log
from node_launcher.node_set.bitcoind.bitcoind_configuration import (
    BitcoindConfiguration
)
from node_launcher.node_set.lib.configuration_file import ConfigurationFile
from node_launcher.port_utilities import get_port


class LndConfiguration(object):
    file: ConfigurationFile

    def __init__(self):
        file_name = 'lnd.conf'
        lnd_dir_path = LND_DIR_PATH[OPERATING_SYSTEM]
        self.file_path = os.path.join(lnd_dir_path, file_name)

    @property
    def args(self):
        if IS_WINDOWS:
            arg_list = [
                f'--configfile={self.file_path}',
            ]
        else:
            arg_list = [
                f'--configfile="{self.file_path}"',
            ]

        arg_list += [
            '--bitcoin.mainnet'
        ]
        return arg_list

    def lncli_arguments(self) -> List[str]:
        args = []
        if self.grpc_port != LND_DEFAULT_GRPC_PORT:
            args.append(f'--rpcserver=127.0.0.1:{self.grpc_port}')
        if self.lnddir != LND_DIR_PATH[OPERATING_SYSTEM]:
            args.append(f'''--lnddir="{self.lnddir}"''')
            args.append(f'--macaroonpath="{self.macaroon_path}"')
            args.append(f'--tlscertpath="{self.tls_cert_path}"')
        return args

    def load(self):
        log.info(
            'lnd configuration_file_path',
            configuration_file_path=self.file_path
        )

        self.file = ConfigurationFile(self.file_path)

    def check(self):
        self.lnddir = LND_DIR_PATH[OPERATING_SYSTEM]

        # Previous versions of the launcher set lnddir in the config file,
        # but it is not a valid key so this helps old users upgrading
        if self.file['lnddir'] is not None:
            self.file['lnddir'] = None

        if self.file['debuglevel'] is None:
            self.file['debuglevel'] = 'info'

        self.file['bitcoin.active'] = True
        self.file['bitcoin.node'] = 'bitcoind'
        bitcoind_conf = BitcoindConfiguration()
        bitcoind_conf.load()
        self.file[
            'bitcoind.rpchost'] = f'127.0.0.1:{bitcoind_conf.rpc_port}'
        self.file['bitcoind.rpcuser'] = bitcoind_conf.file['rpcuser']
        self.file['bitcoind.rpcpass'] = bitcoind_conf.file['rpcpassword']
        self.file['bitcoind.zmqpubrawblock'] = bitcoind_conf.file[
            'zmqpubrawblock']
        self.file['bitcoind.zmqpubrawtx'] = bitcoind_conf.file[
            'zmqpubrawtx']

        if self.file['restlisten'] is None:
            self.rest_port = get_port(LND_DEFAULT_REST_PORT)
            self.file['restlisten'] = f'127.0.0.1:{self.rest_port}'
        else:
            self.rest_port = self.file['restlisten'].split(':')[-1]

        if not self.file['rpclisten']:
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
            'mainnet'
        )
        self.config_snapshot = self.file.snapshot.copy()
        self.file.file_watcher.fileChanged.connect(self.config_file_changed)
        self.file.file_watcher.fileChanged.connect(
            self.bitcoin_config_file_changed)

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
            self.file.file_watcher.addPath(self.file_path)

    def bitcoin_config_file_changed(self):
        # Refresh config file
        self.file.file_watcher.blockSignals(True)
        self.file.populate_cache()
        self.file.file_watcher.blockSignals(False)
        bitcoind_conf = BitcoindConfiguration()
        bitcoind_conf.load()
        self.file[
            'bitcoind.rpchost'] = f'127.0.0.1:{bitcoind_conf.rpc_port}'
        self.file['bitcoind.rpcuser'] = bitcoind_conf.file['rpcuser']
        self.file['bitcoind.rpcpass'] = bitcoind_conf.file['rpcpassword']
        self.file['bitcoind.zmqpubrawblock'] = bitcoind_conf.file[
            'zmqpubrawblock']
        self.file['bitcoind.zmqpubrawtx'] = bitcoind_conf.file[
            'zmqpubrawtx']

    @property
    def node_port(self) -> str:
        if self.file['listen'] is None:
            port = get_port(LND_DEFAULT_PEER_PORT)
            self.file['listen'] = f'127.0.0.1:{port}'
        else:
            if not isinstance(self.file['listen'], list):
                port = self.file['listen'].split(':')[-1]
            else:
                port = self.file['listen'][0].split(':')[-1]
        return port

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

    @property
    def rest_url(self) -> str:
        return f'https://127.0.0.1:{self.rest_port}'

    @property
    def grpc_url(self) -> str:
        return f'127.0.0.1:{self.grpc_port}'

    @property
    def restart_required(self):
        if self.running:
            # Did bitcoin details change
            if self.restart_required:
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

    def test_tls_cert(self):
        context = ssl.create_default_context()
        context.load_verify_locations(cafile=self.tls_cert_path)
        conn = context.wrap_socket(socket.socket(socket.AF_INET),
                                   server_hostname='127.0.0.1')
        conn.connect(('127.0.0.1', int(self.rest_port)))
        cert = conn.getpeercert()
        return cert
