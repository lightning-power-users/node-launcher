from .bitcoind.bitcoind_node import BitcoindNode
from .lib.node_status import NodeStatus
from .lnd.lnd_node import LndNode
from .tor.tor_node import TorNode
from node_launcher.logging import log


class NodeSet(object):
    bitcoind_node: BitcoindNode
    lnd_node: LndNode
    tor_node: TorNode

    def __init__(self):
        self.tor_node = TorNode()
        self.bitcoind_node = BitcoindNode()
        self.lnd_node = LndNode()

        self.tor_node.status.connect(
            self.handle_tor_node_status_change
        )
        self.bitcoind_node.status.connect(
            self.handle_bitcoin_node_status_change
        )

    def start(self):
        log.debug('Starting node set')
        self.tor_node.software.update()

    def handle_tor_node_status_change(self, status):
        if status in [NodeStatus.SOFTWARE_DOWNLOADED,
                      NodeStatus.SOFTWARE_READY]:
            self.bitcoind_node.software.update()
        elif status == NodeStatus.SYNCED:
            self.bitcoind_node.tor_synced = True
            self.bitcoind_node.start_process()
        elif status == NodeStatus.STOPPED:
            self.lnd_node.stop()
            self.bitcoind_node.stop()

    def handle_bitcoin_node_status_change(self, status):
        if status in [NodeStatus.SOFTWARE_DOWNLOADED,
                      NodeStatus.SOFTWARE_READY]:
            if self.lnd_node.current_status is None:
                self.lnd_node.software.update()
        elif status == NodeStatus.SYNCING:
            self.lnd_node.bitcoind_syncing = True
            self.lnd_node.start_process()
        elif status == NodeStatus.STOPPED:
            self.lnd_node.stop()
            self.lnd_node.bitcoind_syncing = False
        elif status == NodeStatus.RESTART:
            self.lnd_node.stop()
            self.bitcoind_node.software.update()
            self.bitcoind_node.start_process()
