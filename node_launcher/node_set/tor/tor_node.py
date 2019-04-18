import os

from node_launcher.constants import TOR_DIR_PATH, OPERATING_SYSTEM
from node_launcher.logging import log
from node_launcher.node_set.lib.network_node import NetworkNode
from node_launcher.node_set.tor.tor_process import TorProcess
from node_launcher.node_set.lnd.lnd import Lnd
from node_launcher.node_set.lib.configuration_file import ConfigurationFile
from node_launcher.node_set.tor.tor_software import TorSoftware


class TorNode(NetworkNode):
    file: ConfigurationFile
    software: TorSoftware
    process: TorProcess

    def __init__(self, lnd: Lnd, configuration_file_path: str = None):
        super().__init__()
        if configuration_file_path is None:
            file_name = 'torrc'
            tor_dir_path = TOR_DIR_PATH[OPERATING_SYSTEM]
            configuration_file_path = os.path.join(tor_dir_path, file_name)
        log.info(
            'tor configuration_file_path',
            configuration_file_path=configuration_file_path
        )

        self.lnd = lnd
        self.bitcoin = lnd.bitcoin
        self.file = ConfigurationFile(path=configuration_file_path, assign_op=' ')
        self.software = TorSoftware()

        # torrc edits
        self.file['ControlPort'] = 9051
        self.file['CookieAuthentication'] = True
        self.file['HiddenServiceDir'] = self.bitcoin_service_directory
        self.file['HiddenServicePort'] = '8333 127.0.0.1:8333'

        # bitcoin.conf edits
        self.bitcoin.file['proxy'] = '127.0.0.1:9050'
        self.bitcoin.file['listen'] = True
        self.bitcoin.file['bind'] = '127.0.0.1'
        self.bitcoin.file['debug'] = 'tor'
        self.bitcoin.file['discover'] = True

        # lnd.conf edits
        self.lnd.file['listen'] = 'localhost'
        self.lnd.file['tor.active'] = True
        self.lnd.file['tor.v3'] = True
        self.lnd.file['tor.streamisolation'] = True

        self.process = TorProcess(self.software.tor, [])
        self.software.ready.connect(self.start_tor)

    def start_tor(self):
        log.debug('Starting Tor')
        self.process.start()

    @property
    def bitcoin_service_directory(self) -> str:
        tor_directory = self.software.downloads_directory_path
        bitcoin_service_directory = os.path.join(tor_directory, 'bitcoin-service')
        return bitcoin_service_directory
