import os
import platform
from typing import Dict

TARGET_RELEASE = 'v0.5.1-beta-rc1'


class OperatingSystem(object):
    def __init__(self, name: str):
        self.name = name.lower()

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return other.name == self.name

    def __ne__(self, other):
        return other.lower() != self.name


DARWIN: OperatingSystem = OperatingSystem('darwin')
LINUX: OperatingSystem = OperatingSystem('linux')
WINDOWS: OperatingSystem = OperatingSystem('windows')
OPERATING_SYSTEM = OperatingSystem(platform.system())

# Only relevant for Windows
LOCALAPPDATA = os.path.abspath(os.environ.get('LOCALAPPDATA', ''))
APPDATA = os.path.abspath(os.environ.get('APPDATA', ''))
PROGRAMS = os.environ.get('Programw6432', '')

BITCOIN_QT_PATH: Dict[OperatingSystem, str] = {
    DARWIN: '/Applications/Bitcoin-Qt.app/Contents/MacOS/Bitcoin-Qt',
    LINUX: 'bitcoind',
    WINDOWS: os.path.join(PROGRAMS, 'Bitcoin', 'bitcoin-qt.exe')
}

NODE_LAUNCHER_DATA_PATH: Dict[OperatingSystem, str] = {
    DARWIN: os.path.expanduser(
        '~/Library/Application Support/Node Launcher/'),
    LINUX: os.path.expanduser('~/.node_launcher'),
    WINDOWS: os.path.join(LOCALAPPDATA, 'Node Launcher')
}

LND_DATA_PATH: Dict[OperatingSystem, str] = {
    DARWIN: '~/Library/Application Support/Lnd/',
    LINUX: '~/.lnd/',
    WINDOWS: os.path.join(LOCALAPPDATA, 'lnd')
}

BITCOIN_DATA_PATH: Dict[OperatingSystem, str] = {
    DARWIN: os.path.expanduser('~/Library/Application Support/Bitcoin/'),
    LINUX: os.path.expanduser('~/.bitcoin'),
    WINDOWS: os.path.join(APPDATA, 'Bitcoin')
}
