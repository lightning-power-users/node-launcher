from PySide2.QtCore import Signal

from node_launcher.node_set.lib.managed_process import ManagedProcess
from node_launcher.node_set.lib.node_status import NodeStatus


class TorProcess(ManagedProcess):
    status = Signal(str)

    def __init__(self, binary: str, args=()):
        super().__init__(binary, args)

    def process_output_line(self, line: str):
        if 'Bootstrapped 0%: Starting' in line:
            self.update_status(NodeStatus.SYNCING)
        elif 'Bootstrapped 100%: Done' in line:
            self.update_status(NodeStatus.SYNCED)
