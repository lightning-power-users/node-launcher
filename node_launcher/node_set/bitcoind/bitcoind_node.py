from _signal import SIGTERM

from psutil import process_iter

from node_launcher.gui.qt import QProcess
from node_launcher.logging import log
from node_launcher.node_set.bitcoind.bitcoind_rpc_client import Proxy
from node_launcher.node_set.lib.network_node import NetworkNode
from node_launcher.node_set.lib.node_status import NodeStatus
from node_launcher.node_set.lib.software import Software
from .bitcoind_process import BitcoindProcess
from .bitcoind_software import BitcoindSoftware
from .bitcoind_configuration import BitcoindConfiguration


class BitcoindNode(NetworkNode):
    configuration: BitcoindConfiguration
    process: BitcoindProcess
    software: Software

    def __init__(self):
        super().__init__(
            network='bitcoin',
            Software=BitcoindSoftware,
            Configuration=BitcoindConfiguration,
            Process=BitcoindProcess
        )
        self.tor_synced = False

    def handle_log_line(self, log_line: str):
        if 'You need to rebuild the database using -reindex to go back to unpruned mode.' in log_line:
            if not self.configuration['prune']:
                self.restart = True
                self.configuration.set_prune(True)
                self.stop()
        elif 'Error: Prune: last wallet synchronisation goes beyond pruned data.' in log_line:
            self.restart = True
            self.configuration['disablewallet'] = True
            self.stop()
        elif 'Bitcoin Core is probably already running.' in log_line:
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
