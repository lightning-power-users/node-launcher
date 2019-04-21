from PySide2.QtCore import QProcess

from node_launcher.logging import log
from node_launcher.node_set.lib.network_node import NetworkNode
from node_launcher.node_set.lib.node_status import NodeStatus
from .tor_configuration import TorConfiguration
from .tor_process import TorProcess
from .tor_software import TorSoftware


class TorNode(NetworkNode):
    current_status: NodeStatus
    software: TorSoftware
    configuration: TorConfiguration
    process: TorProcess
    network = 'tor'

    def __init__(self):
        super().__init__()
        self.current_status = None

        self.software = TorSoftware()
        self.configuration = TorConfiguration()
        self.process = TorProcess(self.software.tor)
        self.connect_events()

    def start(self):
        self.update_status(NodeStatus.STARTED)
        self.software.update()

    def stop(self):
        self.process.kill()
        self.update_status(NodeStatus.STOPPED)

    def connect_events(self):
        self.software.status.connect(self.update_status)
        self.process.status.connect(self.update_status)

    def update_status(self, new_status: NodeStatus):
        new_status = str(new_status)
        log.debug('node change_status',
                  network=self.network,
                  new_status=new_status)
        self.current_status = new_status
        self.status.emit(new_status)

        if new_status == str(NodeStatus.SOFTWARE_READY):
            # Todo: run in threads so they don't block the GUI
            self.update_status(NodeStatus.LOADING_CONFIGURATION)
            self.configuration.load()
            self.update_status(NodeStatus.CHECKING_CONFIGURATION)
            self.configuration.check()
            self.update_status(NodeStatus.CONFIGURATION_READY)
            self.update_status(NodeStatus.STARTING_PROCESS)
            self.process.start()
            self.update_status(NodeStatus.PROCESS_STARTED)
