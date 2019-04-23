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
        self.process = Process(self.software.daemon, self.configuration.args)
        self.connect_events()

    def stop(self):
        self.process.kill()
        self.update_status(NodeStatus.STOPPED)

    def handle_status_change(self, new_status):
        pass

    def connect_events(self):
        self.status.connect(self.handle_status_change)
        self.software.status.connect(self.update_status)
        self.process.status.connect(self.update_status)

    def update_status(self, new_status: NodeStatus):
        log.debug(f'update_status {self.network} node',
                  network=self.network,
                  old_status=self.current_status,
                  new_status=new_status)
        self.current_status = new_status
        self.status.emit(str(new_status))
        self.start_process()

    @property
    def prerequisites_synced(self):
        return True

    def start_process(self):
        software_ready = self.current_status == NodeStatus.SOFTWARE_READY
        if software_ready and self.prerequisites_synced:
            # Todo: run in threads so they don't block the GUI
            self.update_status(NodeStatus.LOADING_CONFIGURATION)
            self.configuration.load()
            self.update_status(NodeStatus.CHECKING_CONFIGURATION)
            self.configuration.check()
            self.update_status(NodeStatus.CONFIGURATION_READY)
            self.update_status(NodeStatus.STARTING_PROCESS)
            self.process.start()
            self.update_status(NodeStatus.PROCESS_STARTED)
