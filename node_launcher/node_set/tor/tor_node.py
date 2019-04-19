from node_launcher.logging import log
from node_launcher.node_set.lib.network_node import NetworkNode
from node_launcher.node_set.lib.node_status import NodeStatus
from node_launcher.node_set.tor.tor_configuration import TorConfiguration
from node_launcher.node_set.tor.tor_process import TorProcess
from node_launcher.node_set.tor.tor_software import TorSoftware


class TorNode(NetworkNode):
    node_status: NodeStatus
    software: TorSoftware
    configuration: TorConfiguration
    process: TorProcess
    network = 'tor'

    def __init__(self):
        super().__init__()
        self.node_status = None

        self.software = TorSoftware()
        self.configuration = TorConfiguration()
        self.process = TorProcess(self.software.tor)
        self.connect_events()

    def connect_events(self):
        self.software.status.connect(self.update_status)
        self.software.status.connect(self.start_process)

    def update_status(self, new_status: NodeStatus):
        self.node_status = new_status
        self.status.emit(new_status)

    def start_process(self, new_status: NodeStatus):
        if new_status == NodeStatus.SOFTWARE_READY:
            log.debug(f'Starting {self.network} node')
            self.process.start()
