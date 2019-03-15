import psutil

from node_launcher.node_set.lnd import Lnd
from node_launcher.services.configuration_file import ConfigurationFile

class Tor(object):
    file: ConfigurationFile  # Figure how to edit this for ! the '=' assignment operator
    software: TorSoftware
    process: Optional[psutil.Process]

    def __init__(self, configuration_file_path: str, lnd: Lnd):
        self.lnd = lnd
        self.bitcoin = lnd.bitcoin
        self.file = ConfigurationFile(configuration_file_path)
        self.software = TorSoftware()

        self.tordir = TOR_DIR_PATH[OPERATING_SYSTEM]

        # TODO figure how to use same Config class for torrc
        # TODO add tor configs using the class object

        #TODO add any relevant Tor methods
