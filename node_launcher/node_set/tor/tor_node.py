from node_launcher.logging import log
from node_launcher.node_set.lib.network_node import NetworkNode
from node_launcher.node_set.tor.tor_configuration import TorConfiguration
from node_launcher.node_set.tor.tor_process import TorProcess
from node_launcher.node_set.tor.tor_software import TorSoftware


class TorNode(NetworkNode):
    software: TorSoftware
    configuration: TorConfiguration
    process: TorProcess
    network = 'tor'

    def __init__(self):
        super().__init__()

        self.software = TorSoftware()
        self.configuration = TorConfiguration()
        self.process = TorProcess(self.software.tor)
        self.connect_events()

    def connect_events(self):
        self.software.ready.connect(self.start_process)

    def start(self):
        self.software.update()

    def start_process(self):
        log.debug(f'Starting {self.network} node')
        self.process.start()
