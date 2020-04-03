from typing import Optional

from node_launcher.constants import OPERATING_SYSTEM
from .bitcoind.bitcoind_node import BitcoindNode
from .lib.hard_drives import Partition
from .lib.node_status import NodeStatus
from .lnd.lnd_node import LndNode
from .tor.tor_node import TorNode
from node_launcher.logging import log


class NodeSet(object):
    tor_node: TorNode
    bitcoind_node: Optional[BitcoindNode]
    lnd_node: LndNode

    def __init__(self, full_node_partition: Partition):

        self.full_node_partition = full_node_partition

        self.tor_node = TorNode(operating_system=OPERATING_SYSTEM)
        if self.full_node_partition:
            self.bitcoind_node = BitcoindNode(operating_system=OPERATING_SYSTEM, partition=self.full_node_partition)
        else:
            self.bitcoind_node = None

        self.lnd_node = LndNode(operating_system=OPERATING_SYSTEM, bitcoind_partition=self.full_node_partition)

        self.tor_node.status.connect(
            self.handle_tor_node_status_change
        )
        if self.bitcoind_node:
            self.bitcoind_node.status.connect(
                self.handle_bitcoind_node_status_change
            )
        self.lnd_node.status.connect(
            self.handle_lnd_node_status_change
        )

    def start(self):
        log.debug('Starting node set')
        self.tor_node.software.update()

    def handle_tor_node_status_change(self, tor_status):
        if tor_status == NodeStatus.RESTART:
            self.start()
        elif tor_status == NodeStatus.SOFTWARE_READY:
            self.tor_node.start_process()
            if self.full_node_partition:
                self.bitcoind_node.software.update()
            else:
                self.lnd_node.software.update()
        elif tor_status == NodeStatus.LIBRARY_ERROR:
            self.tor_node.software.start_update_worker()
        elif tor_status == NodeStatus.SYNCED:
            if self.full_node_partition:
                self.bitcoind_node.tor_synced = True
                self.bitcoind_node.start_process()
            else:
                self.lnd_node.tor_synced = True
                self.lnd_node.start_process()
        elif tor_status == NodeStatus.STOPPED:
            self.lnd_node.stop()
            if self.full_node_partition:
                self.bitcoind_node.stop()

    def handle_bitcoind_node_status_change(self, bitcoind_status):
        if bitcoind_status in [NodeStatus.SOFTWARE_DOWNLOADED,
                               NodeStatus.SOFTWARE_READY]:
            if self.lnd_node.current_status is None:
                self.lnd_node.software.update()
        elif bitcoind_status in [NodeStatus.SYNCING, NodeStatus.SYNCED]:
            self.lnd_node.bitcoind_ready = True
            self.lnd_node.start_process()
        elif bitcoind_status == NodeStatus.SYNCED:
            self.lnd_node.bitcoind_syncing = True
            self.bitcoind_node.configuration['reindex'] = False
            self.lnd_node.start_process()
        elif bitcoind_status == NodeStatus.STOPPED:
            self.lnd_node.stop()
            self.lnd_node.bitcoind_ready = False
        elif bitcoind_status == NodeStatus.RESTART:
            self.lnd_node.stop()
            self.bitcoind_node.software.update()
            self.bitcoind_node.start_process()

    def handle_lnd_node_status_change(self, lnd_status):
        if lnd_status == NodeStatus.STOPPED and self.lnd_node.restart:
            self.lnd_node.restart = False
            self.lnd_node.start_process()

