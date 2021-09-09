from typing import Optional

from node_launcher.gui.qt import QProcess
from node_launcher.constants import OperatingSystem, LND
from node_launcher.app_logging import log
from node_launcher.node_set.lib.network_node import NetworkNode
from node_launcher.node_set.lib.node_status import NodeStatus
from node_launcher.node_set.lnd.lnd_threaded_client import LndThreadedClient
from .lnd_configuration import LndConfiguration
from .lnd_unlocker import LndUnlocker
from .lnd_process import LndProcess
from ..lib.hard_drives import Partition


class LndNode(NetworkNode):
    client: Optional[LndThreadedClient]
    configuration: LndConfiguration
    process: LndProcess

    def __init__(self, operating_system: OperatingSystem, bitcoind_partition: Partition):
        super().__init__(operating_system=operating_system,
                         node_software_name=LND,
                         bitcoind_partition=bitcoind_partition)
        self.bitcoind_partition = bitcoind_partition
        self.client = None
        self.unlocker = None
        self.bitcoind_ready = False
        self.tor_synced = False

    def handle_status_change(self, new_status):
        if new_status == NodeStatus.CONFIGURATION_READY:
            self.client = LndThreadedClient(self.configuration)
            self.client.signals.error.connect(self.handle_error)
            self.unlocker = LndUnlocker(configuration=self.configuration)
        elif new_status == NodeStatus.UNLOCK_READY:
            self.unlocker.auto_unlock_wallet()
        elif new_status == NodeStatus.SYNCING:
            self.client.debug_level()

    def handle_log_line(self, line: str):
        if 'Unable to create chain control: unable to subscribe for zmq block events' in line:
            self.restart = True
        elif 'Unable to start server: unable to fetch filter: unable to fetch cfilter' in line:
            self.restart = True
        elif 'Chain backend synced to tip!' in line:
            self.update_status(NodeStatus.BITCOIND_SYNCED)

    @property
    def prerequisites_synced(self):
        if self.bitcoind_partition:
            return self.bitcoind_ready
        else:
            return self.tor_synced

    def stop(self):
        log.debug('lnd stop', process_state=self.process.state())
        if self.process.state() == QProcess.Running:
            self.process.expecting_shutdown = True
            try:
                self.client.stop()
            except:
                self.process.kill()

    def handle_error(self, error_tuple):
        log.error('lnd_node handle_error')
