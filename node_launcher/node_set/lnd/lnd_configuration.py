import base64
import os
import socket
import ssl
from typing import List

from node_launcher.constants import (
    IS_WINDOWS,
    LND_DEFAULT_GRPC_PORT,
    LND_DEFAULT_PEER_PORT,
    LND_DEFAULT_REST_PORT,
    LND_DIR_PATH,
    OPERATING_SYSTEM,
    TOR_SERVICE_PATH)
from node_launcher.app_logging import log
from node_launcher.node_set.bitcoind.bitcoind_configuration import (
    BitcoindConfiguration
)
from node_launcher.node_set.lib.configuration import Configuration
from node_launcher.node_set.lib.hard_drives import Partition
from node_launcher.port_utilities import get_port
from node_launcher.node_set.lnd.lnd_configuration_keys import keys_info as lnd_keys_info


class LndConfiguration(Configuration):
    
    def __init__(self, bitcoind_partition: Partition):
        file_name = 'lnd.conf'
        lnd_dir_path = LND_DIR_PATH[OPERATING_SYSTEM]
        configuration_file_path = os.path.join(lnd_dir_path, file_name)
        self.bitcoind_partition = bitcoind_partition
        super().__init__(name='lnd', path=configuration_file_path, keys_info=lnd_keys_info)

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

        arg_list += [
            '--bitcoin.mainnet',
            '--profile=9736'
        ]
        return arg_list

    @property
    def cli_args(self) -> List[str]:
        args = []
        if self.grpc_port != LND_DEFAULT_GRPC_PORT:
            args.append(f'--rpcserver=127.0.0.1:{self.grpc_port}')
        if self.lnddir != LND_DIR_PATH[OPERATING_SYSTEM]:
            args.append(f'''--lnddir="{self.lnddir}"''')
            args.append(f'--macaroonpath="{self.macaroon_path}"')
            args.append(f'--tlscertpath="{self.tls_cert_path}"')
        return args

    def check(self):
        self.lnddir = LND_DIR_PATH[OPERATING_SYSTEM]

        # Previous versions of the launcher set lnddir in the config file,
        # but it is not a valid key so this helps old users upgrading
        self.remove_configuration_by_name('lnddir')

        self.set_default_configuration('debuglevel', 'info')

        self['bitcoin.active'] = True

        self['bitcoin.node'] = 'bitcoind'
        bitcoind_conf = BitcoindConfiguration(partition=self.bitcoind_partition)
        bitcoind_conf.load()
        self['bitcoind.rpchost'] = f'127.0.0.1:{bitcoind_conf.rpc_port}'
        self['bitcoind.rpcuser'] = bitcoind_conf['rpcuser']
        self['bitcoind.rpcpass'] = bitcoind_conf['rpcpassword']
        self['bitcoind.zmqpubrawblock'] = bitcoind_conf['zmqpubrawblock']
        self['bitcoind.zmqpubrawtx'] = bitcoind_conf['zmqpubrawtx']

        self.set_default_configuration('restlisten', f'127.0.0.1:{get_port(LND_DEFAULT_REST_PORT)}')
        self.rest_port = self['restlisten'].split(':')[-1]

        self.set_default_configuration('rpclisten', f'127.0.0.1:{get_port(LND_DEFAULT_GRPC_PORT)}')
        self.grpc_port = int(self['rpclisten'].split(':')[-1])

        self.set_default_configuration('tlsextraip', '127.0.0.1')

        self.set_default_configuration('color', '#000000')

        self['tor.active'] = True
        self['tor.v3'] = True
        self['tor.streamisolation'] = True

        self.macaroon_path = os.path.join(
            self.lnddir,
            'data',
            'chain',
            'bitcoin',
            'mainnet'
        )

        hostname_file = os.path.join(TOR_SERVICE_PATH, 'hostname')
        with open(hostname_file, 'r') as f:
            self['externalip'] = f.readline().strip()

    @property
    def node_port(self) -> int:
        self.set_default_configuration('listen', f'127.0.0.1:{get_port(LND_DEFAULT_PEER_PORT)}')
        return int(self['listen'].split(':')[-1])

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
        import qrcode
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
