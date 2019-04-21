from PySide2.QtCore import Signal, QObject

from node_launcher.logging import log
from node_launcher.node_set.lib.node_status import NodeStatus


class NetworkNode(QObject):
    current_status: NodeStatus
    network: str

    status = Signal(str)

    def __init__(self, network: str, Software, Configuration, Process):
        super().__init__()
        self.network = network
        self.current_status = None

        self.software = Software()
        self.configuration = Configuration()
        self.process = Process(self.software.tor)
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
        log.debug(f'{self.network} node change_status',
                  network=self.network,
                  old_status=self.current_status,
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
