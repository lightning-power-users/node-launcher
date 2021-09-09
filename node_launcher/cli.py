import sys
from typing import Optional

from node_launcher.gui.qt import QObject
from node_launcher.app_logging import log
from node_launcher.constants import OPERATING_SYSTEM
from node_launcher.node_set.bitcoind.bitcoind_node import BitcoindNode
from node_launcher.node_set.lib.hard_drives import HardDrives
from node_launcher.node_set.lib.node_status import NodeStatus
from node_launcher.node_set.lnd.lnd_node import LndNode
from node_launcher.node_set.tor.tor_node import TorNode


class CLI(QObject):
    tor_node: TorNode
    bitcoind_node: Optional[BitcoindNode]
    lnd_node: LndNode

    def __init__(self):
        super().__init__()
        self.full_node_partition = HardDrives().get_full_node_partition()
        self.tor_node = TorNode(operating_system=OPERATING_SYSTEM)
        self.bitcoind_node = BitcoindNode(operating_system=OPERATING_SYSTEM, partition=self.full_node_partition)
        self.lnd_node = LndNode(operating_system=OPERATING_SYSTEM, bitcoind_partition=self.full_node_partition)

        self.tor_node.status.connect(
            self.handle_tor_node_status_change
        )
        self.bitcoind_node.status.connect(
            self.handle_bitcoind_node_status_change
        )
        self.lnd_node.status.connect(
            self.handle_lnd_node_status_change
        )

    def start(self):
        self.tor_node.software.update()

    def handle_tor_node_status_change(self, tor_status):
        if tor_status == NodeStatus.SOFTWARE_READY:
            self.bitcoind_node.software.update()

    def handle_bitcoind_node_status_change(self, bitcoind_status):
        if bitcoind_status == NodeStatus.SOFTWARE_READY:
            self.lnd_node.software.update()

    def handle_lnd_node_status_change(self, lnd_status):
        if lnd_status == NodeStatus.SOFTWARE_READY:
            sys.exit(0)


if __name__ == '__main__':

    # sys.excepthook = except_hook

    log.info(
        'constants',
        OPERATING_SYSTEM=OPERATING_SYSTEM
    )

    cli = CLI()
    sys.exit(cli.start())
