import math
import os
from shutil import disk_usage
from typing import Optional

from node_launcher.constants import BITCOIN_DATA_PATH, OPERATING_SYSTEM
from node_launcher.utilities import get_dir_size, get_random_password


class BitcoinConfiguration(object):
    def __init__(self, configuration_path: str = None):
        self.configuration_path = None
        self.datadir: str = None
        self.prune: bool = None
        self.rpcuser: str = None
        self.rpcpassword: str = None
        self.configuration_path: str = configuration_path

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
        configuration_path = self.__configuration_path
        if configuration_path is None:
            self.__configuration_path = os.path.join(BITCOIN_DATA_PATH[OPERATING_SYSTEM], 'bitcoin.conf')
        return self.__configuration_path

    @configuration_path.setter
    def configuration_path(self, configuration_path: str):
        if configuration_path is None:
            configuration_path = os.path.join(BITCOIN_DATA_PATH[OPERATING_SYSTEM], 'bitcoin.conf')
        self.__configuration_path = configuration_path
        parent_directory = os.path.abspath(os.path.join(self.configuration_path, os.pardir))
        if not os.path.isdir(parent_directory):
            os.mkdir(parent_directory)
        if not os.path.isfile(self.configuration_path):
            self.generate_file()

    @property
    def datadir(self) -> str:
        datadir = self.read_property('datadir')
        if datadir is None:
            datadir = BITCOIN_DATA_PATH[OPERATING_SYSTEM]
            self.write_property('datadir', datadir)
        self.__datadir = datadir
        return datadir

    @datadir.setter
    def datadir(self, new_datadir: str):
        if new_datadir is None:
            new_datadir = self.read_property('datadir')
            if new_datadir is None:
                new_datadir = BITCOIN_DATA_PATH[OPERATING_SYSTEM]
            self.__datadir = new_datadir
            return

        old_datadir = self.datadir
        if new_datadir != old_datadir:
            self.__datadir = new_datadir
            if not os.path.isdir(self.datadir):
                os.mkdir(self.datadir)
            self.write_property('datadir', new_datadir)

    @property
    def prune(self) -> bool:
        prune = self.read_property('prune')
        if prune is None:
            prune = self.should_prune()
            self.write_property('prune', str(int(prune)))
            self.write_property('txindex', str(int(not prune)))
        self.__prune = bool(int(prune))
        return self.__prune

    @prune.setter
    def prune(self, new_prune: bool):
        if new_prune is None:
            new_prune = self.read_property('prune')
            self.__prune = new_prune
            return
        new_prune = bool(int(new_prune))
        old_prune = self.prune
        if old_prune != new_prune:
            self.__prune = new_prune
            self.write_property('prune', str(int(new_prune)))
            self.write_property('txindex', str(int(not new_prune)))

    @property
    def rpcuser(self) -> str:
        rpcuser = self.read_property('rpcuser')
        if rpcuser is None:
            rpcuser = 'default_user'
            self.write_property('rpcuser', rpcuser)
        self.__rpcuser = rpcuser
        return self.__rpcuser

    @rpcuser.setter
    def rpcuser(self, new_rpcuser: str):
        if new_rpcuser is None:
            self.__rpcuser = None
            return

        old_rpcuser = self.rpcuser
        if new_rpcuser != old_rpcuser:
            self.__rpcuser = new_rpcuser
            self.write_property('rpcuser', new_rpcuser)

    @property
    def rpcpassword(self) -> str:
        rpcpassword = self.read_property('rpcpassword')
        if rpcpassword is None:
            rpcpassword = get_random_password()
            self.write_property('rpcpassword', rpcpassword)
        self.__rpcpassword = rpcpassword
        return rpcpassword

    @rpcpassword.setter
    def rpcpassword(self, new_rpcpassword: str):
        if new_rpcpassword is None:
            self.__rpcpassword = None
            return

        old_rpcpassword = self.rpcpassword
        if new_rpcpassword != old_rpcpassword:
            self.__rpcpassword = new_rpcpassword
            self.write_property('rpcpassword', new_rpcpassword)
