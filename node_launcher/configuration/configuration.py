from node_launcher.configuration.bitcoin_configuration import \
    BitcoinConfiguration
from node_launcher.configuration.directory_configuration import DirectoryConfiguration
from node_launcher.configuration.port_configuration import PortConfiguration
from node_launcher.node_software.bitcoin_software import BitcoinSoftware
from node_launcher.node_software.lnd_software import LndSoftware


class Configuration(object):
    dir: DirectoryConfiguration

    def __init__(self, network: str, bitcoin_configuration: BitcoinConfiguration):
        self.network = network
        self.ports = PortConfiguration()
        bitcoin_software = BitcoinSoftware()
        lnd_software = LndSoftware()
        self.dir = DirectoryConfiguration(bitcoin_software=bitcoin_software,
                                          lnd_software=lnd_software)
        self.bitcoin = bitcoin_configuration
