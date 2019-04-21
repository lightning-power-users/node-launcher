from node_launcher.node_set.lib.network_node import NetworkNode
from .tor_configuration import TorConfiguration
from .tor_process import TorProcess
from .tor_software import TorSoftware


class TorNode(NetworkNode):
    software: TorSoftware
    configuration: TorConfiguration
    process: TorProcess

    def __init__(self):
        super().__init__(
            network='tor',
            Software=TorSoftware,
            Configuration=TorConfiguration,
            Process=TorProcess
        )
