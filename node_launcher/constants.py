import os
import platform
from typing import Dict


class OperatingSystem(object):
    def __init__(self, name: str):
        self.name = name.lower()

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return other.name == self.name

    def __ne__(self, other):
        return other.lower() != self.name


DARWIN: OperatingSystem = OperatingSystem('darwin')
LINUX: OperatingSystem = OperatingSystem('linux')
WINDOWS: OperatingSystem = OperatingSystem('windows')

BITCOIN_QT_PATH: Dict[OperatingSystem, str] = {
    DARWIN: '/Applications/Bitcoin-Qt.app/Contents/MacOS/Bitcoin-Qt',
    WINDOWS: os.path.join(os.environ.get('Programw6432', ''), 'Bitcoin',
                          'bitcoin-qt.exe')
}

DATA_PATH: Dict[OperatingSystem, str] = {
    DARWIN: os.path.expanduser(
        '~/Library/Application Support/Node Launcher/'),
    WINDOWS: os.path.join(os.path.abspath(os.environ.get('LOCALAPPDATA', '')),
                          'Node Launcher'),
    LINUX: os.path.expanduser('~/.node_launcher')
}

OPERATING_SYSTEM = OperatingSystem(platform.system())
