import os
from os.path import expanduser
import platform
from typing import Dict

NODE_LAUNCHER_RELEASE = '.'.join(map(str, (5, 4, 0)))

TARGET_BITCOIN_RELEASE = 'v0.17.1'
TARGET_LND_RELEASE = 'v0.5.1-beta'


class StringConstant(object):
    def __init__(self, name: str):
        self.name = name.lower()

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return other.name == self.name

    def __ne__(self, other):
        return str(other).lower() != self.name


class Network(StringConstant):
    pass


TESTNET: Network = Network('testnet')
MAINNET: Network = Network('mainnet')


class OperatingSystem(StringConstant):
    pass


DARWIN: OperatingSystem = OperatingSystem('darwin')
LINUX: OperatingSystem = OperatingSystem('linux')
WINDOWS: OperatingSystem = OperatingSystem('windows')
OPERATING_SYSTEM = OperatingSystem(platform.system())

IS_MACOS = OPERATING_SYSTEM == DARWIN
IS_LINUX = OPERATING_SYSTEM == LINUX
IS_WINDOWS = OPERATING_SYSTEM == WINDOWS

# Only relevant for Windows
LOCALAPPDATA = os.path.abspath(os.environ.get('LOCALAPPDATA', ''))
APPDATA = os.path.abspath(os.environ.get('APPDATA', ''))
PROGRAMS = os.environ.get('Programw6432', '')


NODE_LAUNCHER_DATA_PATH: Dict[OperatingSystem, str] = {
    DARWIN: expanduser('~/Library/Application Support/Node Launcher/'),
    LINUX: expanduser('~/.node_launcher'),
    WINDOWS: os.path.join(LOCALAPPDATA, 'Node Launcher')
}

LND_DIR_PATH: Dict[OperatingSystem, str] = {
    DARWIN: expanduser('~/Library/Application Support/Lnd/'),
    LINUX: expanduser('~/.lnd/'),
    WINDOWS: os.path.join(LOCALAPPDATA, 'Lnd')
}

LND_CONF_PATH: Dict[OperatingSystem, str] = {
    DARWIN: expanduser('~/Library/Application Support/Lnd/lnd.conf'),
    LINUX: expanduser('~/.lnd/lnd.conf'),
    WINDOWS: os.path.join(LOCALAPPDATA, r'Lnd\lnd.conf')
}

BITCOIN_DATA_PATH: Dict[OperatingSystem, str] = {
    DARWIN: expanduser('~/Library/Application Support/Bitcoin/'),
    LINUX: expanduser('~/.bitcoin'),
    WINDOWS: os.path.join(APPDATA, 'Bitcoin')
}

BITCOIN_CONF_PATH: Dict[OperatingSystem, str] = {
    DARWIN: expanduser('~/Library/Application Support/Bitcoin/'),
    LINUX: expanduser('~/.bitcoin'),
    WINDOWS: os.path.join(APPDATA, r'Bitcoin\bitcoin.conf')
}

TOR_DATA_PATH: Dict[OperatingSystem, str] = {
    WINDOWS: os.path.join(APPDATA, r'tor'),
    DARWIN: '/var/tmp/dist/tor/etc/tor/'
}

TOR_TORRC_PATH: Dict[OperatingSystem, str] = {
    WINDOWS: os.path.join(APPDATA, r'tor\torrc'),
    DARWIN: '/var/tmp/dist/tor/etc/tor/torrc'
}

TOR_PATH: Dict[OperatingSystem, str] = {
    WINDOWS: os.path.join(LOCALAPPDATA, 'tor'),
    DARWIN: expanduser('~/Library/Application Support/Tor')
}

TOR_EXE_PATH: Dict[OperatingSystem, str] = {
    WINDOWS: os.path.join(LOCALAPPDATA, r'tor\tor\tor.exe')
}

UPGRADE = 'Please download the latest version of the Node Launcher: ' \
                    '<a href="https://github.com/PierreRochard/node-launcher/releases/">' \
                    'https://github.com/PierreRochard/node-launcher/releases' \
                    '</a>'

GIGABYTE = 1000000000

if IS_WINDOWS:
    from keyring.backends.Windows import WinVaultKeyring
    keyring = WinVaultKeyring()

if IS_MACOS:
    from keyring.backends.OS_X import Keyring
    keyring = Keyring()

if IS_LINUX:
    from keyring.backends.SecretService import Keyring
    keyring = Keyring()

# How many megabytes to keep
# Total Bitcoin (mainnet) data directory size minus blocks is ~3 GB
# We are targeting 10 GB, so 10 - 3 = 7
MAINNET_PRUNE = 7000

TESTNET_PRUNE = 1000

BITCOIN_TESTNET_PEER_PORT = 18333
BITCOIN_MAINNET_PEER_PORT = 8333

BITCOIN_TESTNET_RPC_PORT = 18332
BITCOIN_MAINNET_RPC_PORT = 8332

LND_DEFAULT_PEER_PORT = 9735
LND_DEFAULT_GRPC_PORT = 10009
LND_DEFAULT_REST_PORT = 8080
