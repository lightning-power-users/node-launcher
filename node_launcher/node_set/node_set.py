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
        self.lnd_node.process.signals.unprune.connect(self.handle_unprune)

    def start(self):
        log.debug('Starting node set')
        self.tor_node.software.update()

    def handle_tor_node_status_change(self, tor_status):
        if tor_status == NodeStatus.RESTART:
            self.start()
        elif tor_status in [NodeStatus.SOFTWARE_DOWNLOADED,
                            NodeStatus.SOFTWARE_READY]:
            self.bitcoind_node.software.update()
        elif tor_status == NodeStatus.LIBRARY_ERROR:
            # raise Exception
            self.tor_node.software.start_update_worker()
        elif tor_status == NodeStatus.SYNCED:
            self.bitcoind_node.tor_synced = True
            self.bitcoind_node.start_process()
        elif tor_status == NodeStatus.STOPPED:
            self.lnd_node.stop()
            self.bitcoind_node.stop()

    def handle_bitcoin_node_status_change(self, bitcoind_status):
        if bitcoind_status in [NodeStatus.SOFTWARE_DOWNLOADED,
                               NodeStatus.SOFTWARE_READY]:
            if self.lnd_node.current_status is None:
                self.lnd_node.software.update()
        elif bitcoind_status == NodeStatus.SYNCING:
            self.lnd_node.bitcoind_syncing = True
            self.lnd_node.start_process()
        elif bitcoind_status == NodeStatus.SYNCED:
            self.lnd_node.bitcoind_syncing = True
            self.bitcoind_node.configuration['reindex'] = False
            self.lnd_node.start_process()
        elif bitcoind_status == NodeStatus.STOPPED:
            self.lnd_node.stop()
            self.lnd_node.bitcoind_syncing = False
        elif bitcoind_status == NodeStatus.RESTART:
            self.lnd_node.stop()
            self.bitcoind_node.software.update()
            self.bitcoind_node.start_process()

    def handle_unprune(self, height: int):
        self.lnd_node.stop()
        self.bitcoind_node.unprune(height)
