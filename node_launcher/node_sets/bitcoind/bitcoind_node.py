from _signal import SIGTERM

from PySide2.QtCore import QProcess
from psutil import process_iter

from node_launcher.constants import OperatingSystem, BITCOIND
from node_launcher.logging import log
from node_launcher.node_set.bitcoind.bitcoind_rpc_client import Proxy
from node_launcher.node_set.lib.network_node import NetworkNode
from node_launcher.node_set.lib.node_status import NodeStatus
from node_launcher.node_set.lib.software import Software
from .bitcoind_process import BitcoindProcess
from .bitcoind_configuration import BitcoindConfiguration
from ..lib.hard_drives import Partition


class BitcoindNode(NetworkNode):
    configuration: BitcoindConfiguration
    process: BitcoindProcess
    software: Software

    def __init__(self, operating_system: OperatingSystem, partition: Partition):
        super().__init__(operating_system=operating_system,
                         node_software_name=BITCOIND,
                         bitcoind_partition=partition)
        self.tor_synced = False

    def handle_log_line(self, log_line: str):
        if 'Bitcoin Core is probably already running.' in log_line:
            for proc in process_iter():
                try:
                    name = proc.name()
                    if name == 'bitcoind':
                        proc.send_signal(SIGTERM)
                except Exception as e:
                    log.debug('proc exception', {'exception': e})
                    pass
            self.update_status(NodeStatus.RESTART)

    @property
    def bitcoin_cli(self) -> str:
        command = [
            f'"{self.software.bitcoin_cli}"',
            f'-conf="{self.configuration.path}"',
        ]
        return ' '.join(command)

    @property
    def prerequisites_synced(self):
        return self.tor_synced

    def stop(self):
        if self.process.state() == QProcess.Running:
            self.process.expecting_shutdown = True
            client = Proxy(btc_conf_file=self.configuration.file.path,
                           service_port=self.configuration.rpc_port)
            try:
                client.call('stop')
            except:
                self.process.terminate()
