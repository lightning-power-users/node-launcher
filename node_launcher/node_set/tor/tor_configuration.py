import os

from node_launcher.constants import TOR_DIR_PATH, OPERATING_SYSTEM, TOR_SERVICE_PATH
from node_launcher.logging import log
from node_launcher.node_set.lib.configuration_file import ConfigurationFile


class TorConfiguration(object):
    def __init__(self):
        self.file = None

    @property
    def args(self):
        return []

    def load(self):
        file_name = 'torrc'
        tor_dir_path = TOR_DIR_PATH[OPERATING_SYSTEM]
        configuration_file_path = os.path.join(tor_dir_path, file_name)
        log.info(
            'Loading tor configuration file',
            configuration_file_path=configuration_file_path
        )
        self.file = ConfigurationFile(path=configuration_file_path, assign_op=' ')

    def check(self):
        # torrc edits
        self.file['ControlPort'] = 9051
        self.file['CookieAuthentication'] = True
        self.file['HiddenServiceDir'] = TOR_SERVICE_PATH
        self.file['HiddenServicePort'] = '8333 127.0.0.1:8333'
