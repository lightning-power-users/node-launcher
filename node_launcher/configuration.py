from random import choice
from string import ascii_lowercase, digits

from node_launcher.directory_configuration import DirectoryConfiguration
from node_launcher.port_configuration import PortConfiguration


class Configuration(object):
    def __init__(self, network: str, pruned: bool):
        self.bitcoin_rpc_user = 'user'
        self.bitcoin_rpc_password = ''.join(choice(ascii_lowercase + digits)
                                            for _ in range(16))
        self.network = network
        self.pruned = pruned
        self.ports = PortConfiguration()
        self.dir = DirectoryConfiguration(network, pruned)
