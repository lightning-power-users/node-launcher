import os
from typing import Dict

BITCOIN_QT_PATH: Dict[str, str] = {
    'Darwin': '/Applications/Bitcoin-Qt.app/Contents/MacOS/Bitcoin-Qt'
}

DATA_PATH: Dict[str, str] = {
    'Darwin': os.path.expanduser('~/Library/Application Support/Node Launcher/'),
    'Windows': os.path.join(os.environ['LOCALAPPDATA'], 'Node Launcher'),
    'Linux': os.path.expanduser('~/.node_launcher')
}
