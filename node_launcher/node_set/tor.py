import os

from PySide2.QtCore import QProcess

from .lnd import Lnd
from node_launcher.services.configuration_file import ConfigurationFile
from node_launcher.services.tor_software import TorSoftware


class Tor(object):
    file: ConfigurationFile
    software: TorSoftware
    process: QProcess

    def __init__(self, configuration_file_path: str, lnd: Lnd):
        self.lnd = lnd
        self.bitcoin = lnd.bitcoin
        self.file = ConfigurationFile(path=configuration_file_path, assign_op=' ')
        self.software = TorSoftware()

        tor_directory = self.software.downloads_directory_path
        bitcoin_service_directory = os.path.join(tor_directory, 'bitcoin-service')

        # torrc edits
        self.file['ControlPort'] = 9051
        self.file['CookieAuthentication'] = True
        self.file['HiddenServiceDir'] = bitcoin_service_directory
        self.file['HiddenServicePort'] = '8333 127.0.0.1:8333'

        # bitcoin.conf edits
        self.bitcoin.file['proxy'] = '127.0.0.1:9050'
        self.bitcoin.file['listen'] = True
        self.bitcoin.file['bind'] = '127.0.0.1'
        self.bitcoin.file['debug'] = 'tor'

        # lnd.conf edits
        self.lnd.file['listen'] = 'localhost'
        self.lnd.file['tor.active'] = True
        self.lnd.file['tor.v3'] = True
        self.lnd.file['tor.streamisolation'] = True
        hostname_file = os.path.join(bitcoin_service_directory, 'hostname')
        with open(hostname_file, 'r') as f:
            self.lnd.file['externalip'] = f.readline().strip()

        self.process = QProcess()
        self.process.setProgram(self.software.tor)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
