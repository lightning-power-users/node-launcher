import psutil, os

from node_launcher.node_set.lnd import Lnd
from node_launcher.services.configuration_file import ConfigurationFile
from node_launcher.constants import (
    IS_LINUX,
    IS_MACOS,
    IS_WINDOWS,
    LND_DIR_PATH,
    TOR_DATA_PATH,
    OPERATING_SYSTEM,
)

class Tor(object):
    file: ConfigurationFile
    #software: TorSoftware
    #process: Optional[psutil.Process]

    def __init__(self, configuration_file_path: str, lnd: Lnd):
        self.lnd = lnd
        self.bitcoin = lnd.bitcoin
        self.file = ConfigurationFile(configuration_file_path, ' ')
        #self.software = TorSoftware()

        self.tordir = TOR_DATA_PATH[OPERATING_SYSTEM]

    def launch(self):
        pass
