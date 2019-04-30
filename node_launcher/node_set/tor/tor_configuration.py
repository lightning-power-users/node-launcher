import os

from node_launcher.constants import TOR_DIR_PATH, OPERATING_SYSTEM, TOR_SERVICE_PATH
from node_launcher.node_set.lib.configuration import Configuration


class TorConfiguration(Configuration):
    def __init__(self):
        file_name = 'torrc'
        tor_dir_path = TOR_DIR_PATH[OPERATING_SYSTEM]
        configuration_file_path = os.path.join(tor_dir_path, file_name)
        super().__init__(name='tor', path=configuration_file_path, assign_op=' ')

    @property
    def args(self):
        return []

    def check(self):
        # torrc edits
        self['ControlPort'] = 9051
        self['CookieAuthentication'] = True
        self['HiddenServiceDir'] = TOR_SERVICE_PATH
        self['HiddenServicePort'] = '8333 127.0.0.1:8333'
