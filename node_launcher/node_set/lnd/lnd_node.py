from PySide2.QtCore import QProcess

from node_launcher.node_set.lib.network_node import NetworkNode
from node_launcher.node_set.lib.node_status import NodeStatus
from node_launcher.node_set.lnd.lnd_threaded_client import LndThreadedClient
from .lnd_configuration import LndConfiguration
from .lnd_unlocker import LndUnlocker
from .lnd_process import LndProcess
from .lnd_software import LndSoftware


class LndNode(NetworkNode):
    client: LndThreadedClient
    configuration: LndConfiguration
    process: LndProcess
    software: LndSoftware

    def __init__(self):
        super().__init__(
            network='lnd',
            Software=LndSoftware,
            Configuration=LndConfiguration,
            Process=LndProcess
        )
        self.client = None
        self.unlocker = None
        self.bitcoind_syncing = False

    def handle_status_change(self, new_status):
        if new_status == NodeStatus.CONFIGURATION_READY:
            self.client = LndThreadedClient(self.configuration)
            self.unlocker = LndUnlocker(configuration=self.configuration)
        elif new_status == NodeStatus.UNLOCK_READY:
            self.unlocker.auto_unlock_wallet()
        elif new_status == NodeStatus.SYNCING:
            self.client.debug_level()

    @property
    def prerequisites_synced(self):
        return self.bitcoind_syncing

    def stop(self):
        if self.process.state() == QProcess.Running:
            self.process.expecting_shutdown = True
            try:
                self.client.stop()
            except:
                self.process.kill()
