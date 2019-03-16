import psutil

from node_launcher.node_set.lnd import Lnd
from node_launcher.services.configuration_file import ConfigurationFile
from node_launcher.constants import (
    IS_LINUX,
    IS_MACOS,
    IS_WINDOWS,
    LND_DIR_PATH,
    TOR_PATH, # Change to TOR_DIR_PATH
    OPERATING_SYSTEM,
    #BITCOIN_DATA_PATH,
    #BITCOIN_CONF_PATH,
    #TOR_DATA_PATH,
    #TOR_TORRC_PATH,
    #LND_CONF_PATH,
    #TOR_EXE_PATH,
)

class Tor(object):
    file: ConfigurationFile
    software: TorSoftware
    process: Optional[psutil.Process]

    def __init__(self, configuration_file_path: str, lnd: Lnd):
        self.lnd = lnd
        self.bitcoin = lnd.bitcoin
        self.file = ConfigurationFile(configuration_file_path, ' ')
        self.software = TorSoftware()

        self.tordir = TOR_DIR_PATH[OPERATING_SYSTEM]

        self.file['ControlPort'] = '9051'
        self.file['CookieAuthentication'] = '1'
        self.file['HiddenServiceDir'] = os.path.join(self.tordir, 'bitcoin-service')
        self.file['HiddenServicePort'] = '8333 127.0.0.1:8333'
        self.file['HiddenServicePort'] = '18333 127.0.0.1:18333'

        # TODO add lnd- & bitcoind-specific configs
        # TODO add any relevant Tor methods

    def launch(self):
        pass
