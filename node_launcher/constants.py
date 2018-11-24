import os
from typing import Dict

BITCOIN_QT_PATH: Dict[str, str] = {
    'Darwin': '/Applications/Bitcoin-Qt.app/Contents/MacOS/Bitcoin-Qt',
    'Windows': os.path.join(os.environ.get('Programw6432'), 'Bitcoin/bitcoin-qt')
}

DATA_PATH: Dict[str, str] = {
    'Darwin': os.path.expanduser('~/Library/Application Support/Node Launcher/'),
    'Windows': os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Node Launcher'),
    'Linux': os.path.expanduser('~/.node_launcher')
}
