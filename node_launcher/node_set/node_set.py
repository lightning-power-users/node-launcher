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

        self.tor_node.status.connect(self.handle_tor_node_status_change)
        self.bitcoin.status.connect(self.handle_bitcoin_node_status_change)
        self.lnd.status.connect(self.handle_lnd_node_status_change)

    def start(self):
        log.debug('Starting node set')
        self.tor_node.start()

    def handle_tor_node_status_change(self, status):
        if status == NodeStatus.SOFTWARE_DOWNLOADED:
            self.bitcoin.software.update()

    def handle_bitcoin_node_status_change(self, status):
        if status == NodeStatus.SOFTWARE_DOWNLOADED:
            self.lnd.software.update()

    def handle_lnd_node_status_change(self, status):
        pass

    def start_lnd(self):
        hostname_file = os.path.join(TOR_SERVICE_PATH, 'hostname')
        with open(hostname_file, 'r') as f:
            self.lnd.file['externalip'] = f.readline().strip()
        self.lnd.software.run()

