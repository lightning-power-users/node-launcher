from PySide2.QtCore import QProcess

from node_launcher.node_set.bitcoind.bitcoind_rpc_client import Proxy
from node_launcher.node_set.lib.network_node import NetworkNode
from .bitcoind_process import BitcoindProcess
from .bitcoind_software import BitcoindSoftware
from .bitcoind_configuration import BitcoindConfiguration


class BitcoindNode(NetworkNode):
    configuration: BitcoindConfiguration
    process: BitcoindProcess
    software: BitcoindSoftware

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
