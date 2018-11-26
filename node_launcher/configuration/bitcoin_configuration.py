import math
import os
from shutil import disk_usage
from typing import Optional

from node_launcher.constants import BITCOIN_DATA_PATH, OPERATING_SYSTEM
from node_launcher.utilities import get_dir_size


class BitcoinConfiguration(object):
    def __init__(self, configuration_path: str = None):
        if configuration_path is None:
            configuration_path = os.path.join(BITCOIN_DATA_PATH[OPERATING_SYSTEM], 'bitcoin.conf')
        self.configuration_path = configuration_path
        self.datadir = self.read_property('datadir')
        if self.datadir is None:
            self.datadir = BITCOIN_DATA_PATH[OPERATING_SYSTEM]

        self.prune = self.read_property('prune')
        if self.prune is None:
            self.prune = self.should_prune()
        else:
            self.prune = bool(self.prune)

    def should_prune(self) -> bool:
        _, _, free_bytes = disk_usage(os.path.realpath(self.datadir))
        bitcoin_bytes = get_dir_size(self.datadir)
        free_bytes += bitcoin_bytes
        gigabyte = 1000000000
        free_gb = math.floor(free_bytes / gigabyte)
        bitcoin_gb = math.ceil(bitcoin_bytes / gigabyte)
        if free_gb < 300 and bitcoin_gb > 10:
            raise Exception('Un-pruned bitcoin chain data '
                            'but not enough space to finish IBD')
        return free_gb < 300

    def generate_file(self):
        with open(self.configuration_path, 'w') as f:
            f.write('# Auto-generated with Node Launcher')
            f.flush()

    def write_property(self, name: str, value: str):
        if ' ' in value and not value.startswith('"'):
            value = f'"{value}"'
        property_string = f'{name}={value}\n'

        with open(self.configuration_path, 'r') as f:
            lines = f.readlines()

        property_lines = [line_number for line_number, l in enumerate(lines)
                          if l.startswith(name)]
        if len(property_lines) > 1:
            raise Exception(
                f'Multiple occurrences of {name} in {self.configuration_path}')
        elif len(property_lines) == 1:
            property_line = property_lines[0]
            lines[property_line] = property_string
        else:
            lines.append(property_string)

        with open(self.configuration_path, 'w') as f:
            f.writelines(lines)

    def read_property(self, name: str) -> Optional[str]:
        with open(self.configuration_path, 'r') as f:
            lines = f.readlines()
        property_lines = [l for l in lines if l.startswith(name)]
        if len(property_lines) > 1:
            raise Exception(
                f'Multiple occurrences of {name} in {self.configuration_path}')
        elif len(property_lines) == 1:
            property_line = property_lines[0]
            value = property_line.split('=')[1:]
            value = '='.join(value).strip()
            return value.replace('"', '')
        else:
            return None

    @property
    def configuration_path(self) -> str:
        return self.__configuration_path

    @configuration_path.setter
    def configuration_path(self, configuration_path: str):
        self.__configuration_path = configuration_path

        if not os.path.isfile(self.configuration_path):
            self.generate_file()

    @property
    def datadir(self) -> Optional[str]:
        try:
            return self.__datadir
        except AttributeError:
            return None

    @datadir.setter
    def datadir(self, new_datadir: str):
        if new_datadir is None:
            self.__datadir = None
            return

        old_datadir = self.datadir
        if new_datadir != old_datadir:
            self.__datadir = new_datadir
            if not os.path.isdir(self.datadir):
                os.mkdir(self.datadir)
            self.write_property('datadir', new_datadir)

    @property
    def prune(self) -> Optional[bool]:
        try:
            return self.__prune
        except AttributeError:
            return None

    @prune.setter
    def prune(self, new_prune: bool):
        if new_prune is None:
            self.__prune = None
            return
        new_prune = bool(int(new_prune))
        old_prune = self.prune
        if old_prune != new_prune:
            self.__prune = new_prune
            self.write_property('prune', str(int(new_prune)))
            self.write_property('txindex', str(int(not new_prune)))
