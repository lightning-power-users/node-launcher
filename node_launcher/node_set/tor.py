import psutil, os

from node_launcher.node_set.lnd import Lnd
from node_launcher.services.configuration_file import ConfigurationFile
from node_launcher.constants import (
    IS_LINUX,
    IS_MACOS,
    IS_WINDOWS,
    LND_DIR_PATH,
    TOR_DIR_PATH,
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

        self.tordir = TOR_DIR_PATH[OPERATING_SYSTEM]

        # torrc edits
        self.file['ControlPort'] = '9051'
        self.file['CookieAuthentication'] = '1'
        self.file['HiddenServiceDir'] = os.path.join(self.tordir, 'bitcoin-service')
        self.file['HiddenServicePort'] = '8333 127.0.0.1:8333'
        self.file['HiddenServicePort'] = '18333 127.0.0.1:18333'

        # bitcoin.conf edits
        self.bitcoin.file['proxy'] = '127.0.0.1:9050'
        self.bitcoin.file['listen'] = '1'
        self.bitcoin.file['bind'] = '127.0.0.1'
        self.bitcoin.file['debug'] = 'tor'

        # lnd.conf edits
        self.lnd.file['listen'] = 'localhost'
        self.lnd.file['tor.active'] = '1'
        self.lnd.file['tor.v3'] = '1'
        self.lnd.file['tor.streamisolation'] = '1'


    def launch(self):
        pass
