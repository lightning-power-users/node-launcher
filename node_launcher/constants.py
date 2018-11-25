import os
from typing import Dict

BITCOIN_QT_PATH: Dict[str, str] = {
    'darwin': '/Applications/Bitcoin-Qt.app/Contents/MacOS/Bitcoin-Qt',
    'windows': os.path.join(os.environ.get('Programw6432', ''), 'Bitcoin', 'bitcoin-qt.exe')
}

DATA_PATH: Dict[str, str] = {
    'darwin': os.path.expanduser('~/Library/Application Support/Node Launcher/'),
    'windows': os.path.join(os.path.abspath(os.environ.get('LOCALAPPDATA', '')), 'Node Launcher'),
    'linux': os.path.expanduser('~/.node_launcher')
}
