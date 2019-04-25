from node_launcher.node_set.lib.managed_process import ManagedProcess
from node_launcher.node_set.lib.network_node import NetworkNode
from node_launcher.node_set.lib.node_status import NodeStatus
from .tor_configuration import TorConfiguration
from .tor_software import TorSoftware


class TorNode(NetworkNode):
    software: TorSoftware
    configuration: TorConfiguration
    process: ManagedProcess

    def __init__(self):
        super().__init__(
            network='tor',
            Software=TorSoftware,
            Configuration=TorConfiguration,
            Process=ManagedProcess
        )

    def handle_log_line(self, log_line: str):
        if 'Bootstrapped 0%: Starting' in log_line:
            self.update_status(NodeStatus.SYNCING)
        elif 'Bootstrapped 100%: Done' in log_line:
            self.update_status(NodeStatus.SYNCED)
