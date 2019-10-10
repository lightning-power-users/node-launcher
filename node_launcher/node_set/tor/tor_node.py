from _signal import SIGTERM

from psutil import process_iter, AccessDenied

from node_launcher.logging import log
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
        elif 'Bootstrapped 100% (done): Done' in log_line:
            self.update_status(NodeStatus.SYNCED)
        elif log_line.startswith('dyld: Library not loaded'):
            self.update_status(NodeStatus.LIBRARY_ERROR)
        elif ('Address already in use. Is Tor already running' in log_line
                or 'Failed to bind one of the listener ports.' in log_line):
            for proc in process_iter():
                try:
                    for conns in proc.connections(kind='inet'):
                        if conns.laddr.port in (9050, 9051):
                            proc.send_signal(SIGTERM)
                except Exception as e:
                    log.debug('proc exception', {'exception': e})
                    pass
            self.update_status(NodeStatus.RESTART)
