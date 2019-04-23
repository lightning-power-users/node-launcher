import os

from .bitcoind.bitcoind_node import BitcoindNode
from .lib.node_status import NodeStatus
from .lnd.lnd_node import LndNode
from .tor.tor_node import TorNode
from node_launcher.constants import TOR_SERVICE_PATH
from node_launcher.logging import log


class NodeSet(object):
    bitcoind_node: BitcoindNode
    lnd_node: LndNode
    tor_node: TorNode

    def __init__(self):
        self.tor_node = TorNode()
        self.bitcoind_node = BitcoindNode()
        self.lnd_node = LndNode()

        self.tor_node.status.connect(self.handle_tor_node_status_change)
        self.bitcoind_node.status.connect(self.handle_bitcoin_node_status_change)
        self.lnd_node.status.connect(self.handle_lnd_node_status_change)

    def start(self):
        log.debug('Starting node set')
        self.tor_node.start()

    def handle_tor_node_status_change(self, status):
        if status == NodeStatus.SOFTWARE_DOWNLOADED:
            self.bitcoind_node.software.update()
        elif status == NodeStatus.SYNCED:
            self.bitcoind_node.start()

    def handle_bitcoin_node_status_change(self, status):
        if status == NodeStatus.SOFTWARE_DOWNLOADED:
            self.lnd_node.software.update()
        elif status == NodeStatus.SYNCED:
            self.lnd_node.start()

    def handle_lnd_node_status_change(self, status):
        pass

    def start_lnd(self):
        hostname_file = os.path.join(TOR_SERVICE_PATH, 'hostname')
        with open(hostname_file, 'r') as f:
            self.lnd_node.file['externalip'] = f.readline().strip()
        self.lnd_node.software.run()

