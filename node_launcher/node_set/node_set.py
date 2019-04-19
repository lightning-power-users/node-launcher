import os

from .bitcoind.bitcoin import Bitcoin
from .lib.node_status import NodeStatus
from .lnd.lnd import Lnd
from .tor.tor_node import TorNode
from node_launcher.constants import TOR_SERVICE_PATH
from node_launcher.logging import log


class NodeSet(object):
    bitcoin: Bitcoin
    lnd: Lnd
    tor_node: TorNode

    def __init__(self):
        self.tor_node = TorNode()
        self.bitcoin = Bitcoin()
        self.lnd = Lnd(bitcoin=self.bitcoin)

        self.tor_node.software.status.connect(self.download_bitcoin)
        self.bitcoin.software.status.connect(self.download_lnd)

        self.bitcoin.process.synced.connect(self.start_lnd)

    def start(self):
        log.debug('Starting node set')
        self.tor_node.software.update()

    def download_bitcoin(self, status):
        if status == NodeStatus.INSTALLING_SOFTWARE:
            self.bitcoin.software.update()

    def download_lnd(self, status):
        if status == NodeStatus.INSTALLING_SOFTWARE:
            self.lnd.software.update()

    def start_lnd(self):
        hostname_file = os.path.join(TOR_SERVICE_PATH, 'hostname')
        with open(hostname_file, 'r') as f:
            self.lnd.file['externalip'] = f.readline().strip()
        self.lnd.software.run()

