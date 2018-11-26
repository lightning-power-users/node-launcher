import os

from node_launcher.constants import BITCOIN_DATA_PATH, OPERATING_SYSTEM


class BitcoinConfiguration(object):
    def __init__(self, configuration_path: str):
        self.configuration_path = configuration_path
        self.datadir = self.read_property('datadir')
        if self.datadir is None:
            self.datadir = BITCOIN_DATA_PATH[OPERATING_SYSTEM]

    def generate_file(self):
        with open(self.configuration_path, 'w') as f:
            f.write('# Auto-generated with Node Launcher')
            f.flush()

    def write_property(self, name: str, value: str):
        if ' ' in value:
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

    def read_property(self, name: str):
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
            return value
        else:
            return None

    @property
    def configuration_path(self):
        return self.__configuration_path

    @configuration_path.setter
    def configuration_path(self, configuration_path):
        self.__configuration_path = configuration_path

        if not os.path.isfile(self.configuration_path):
            self.generate_file()

    @property
    def datadir(self):
        return self.__datadir

    @datadir.setter
    def datadir(self, datadir):
        self.__datadir = datadir
        self.write_property('datadir', datadir)
        if not os.path.isdir(self.datadir):
            os.mkdir(self.datadir)
