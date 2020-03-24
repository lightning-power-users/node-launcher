from typing import Optional

from node_launcher.constants import OPERATING_SYSTEM
from .bitcoind.bitcoind_node import BitcoindNode
from .lib.hard_drives import HardDrives
from .lib.node_status import NodeStatus
from .lnd.lnd_node import LndNode
from .tor.tor_node import TorNode
from node_launcher.logging import log


class NodeSet(object):
    tor_node: TorNode
    bitcoind_node: Optional[BitcoindNode]
    lnd_node: LndNode

    is_full_node: bool = False

    def __init__(self):
        self.is_full_node = self.can_full_node()

        self.tor_node = TorNode(operating_system=OPERATING_SYSTEM)
        self.bitcoind_node = BitcoindNode(operating_system=OPERATING_SYSTEM)
        self.lnd_node = LndNode(operating_system=OPERATING_SYSTEM)

        self.tor_node.status.connect(
            self.handle_tor_node_status_change
        )
        self.bitcoind_node.status.connect(
            self.handle_bitcoind_node_status_change
        )
        self.lnd_node.status.connect(
            self.handle_lnd_node_status_change
        )

    def can_full_node(self) -> bool:
        hard_drives = HardDrives()
        partitions = hard_drives.list_partitions()
        print(partitions)
        # is_big_enough = not hard_drives.should_prune(big_drive.mountpoint)
        # log.info(
        #     'can_full_node',
        #     big_drive_mountpoint=big_drive.mountpoint,
        #     is_big_enough=is_big_enough
        # )
        # return is_big_enough

    def start(self):
        log.debug('Starting node set')
        self.tor_node.software.update()

    def handle_tor_node_status_change(self, tor_status):
        if tor_status == NodeStatus.RESTART:
            self.start()
        elif tor_status in [NodeStatus.SOFTWARE_DOWNLOADED,
                            NodeStatus.SOFTWARE_READY]:
            self.lnd_node.software.update()
        elif tor_status == NodeStatus.LIBRARY_ERROR:
            self.tor_node.software.start_update_worker()
        elif tor_status == NodeStatus.SYNCED:
            self.lnd_node.start_process()
        elif tor_status == NodeStatus.STOPPED:
            self.lnd_node.stop()

    def handle_bitcoind_node_status_change(self, bitcoind_status):
        pass

    def handle_lnd_node_status_change(self, lnd_status):
        if lnd_status == NodeStatus.STOPPED and self.lnd_node.restart:
            self.lnd_node.restart = False
            self.lnd_node.start_process()

