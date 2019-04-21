from typing import List

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

    @property
    def bitcoin_cli(self) -> str:
        command = [
            f'"{self.software.bitcoin_cli}"',
            f'-conf="{self.configuration.file_path}"',
        ]
        return ' '.join(command)

    @property
    def args(self) -> List[str]:
        return [f'-conf={self.configuration.file_path}']

