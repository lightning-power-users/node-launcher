import os
from os.path import isfile, isdir, pardir

from node_launcher.constants import NODE_LAUNCHER_RELEASE

exceptions = ['path']


class ConfigurationFile(object):
    def __init__(self, path):
        self.path = path
        parent = os.path.abspath(os.path.join(path, pardir))
        if not isdir(parent):
            os.mkdir(parent)
        if not isfile(self.path):
            with open(self.path, 'w') as f:
                f.write('# Auto-Generated Configuration File\n\n')
                f.write(f'# Node Launcher version {NODE_LAUNCHER_RELEASE}\n\n')
                f.flush()

    def __getattr__(self, name):
        with open(self.path, 'r') as f:
            lines = f.readlines()
        property_lines = [l for l in lines if l.startswith(name)]
        if len(property_lines) > 1:
            raise Exception(
                f'Multiple occurrences of {name} in {self.path}')
        elif len(property_lines) == 1:
            property_line = property_lines[0]
            value = property_line.split('=')[1:]
            value = '='.join(value).strip()
            value = value.replace('"', '')
            if len(value) == 1 and value.isdigit():
                value = bool(int(value))
            return value
        else:
            return None

    def __setattr__(self, name, value):
        if name in exceptions:
            super().__setattr__(name, value)
            return

        if isinstance(value, str):
            pass
        elif isinstance(value, bool):
            value = str(int(value))
        elif isinstance(value, int):
            value = str(value)
        else:
            raise NotImplementedError(f'setattr for {type(value)}')

        self.write_property(name, value)

    def write_property(self, name: str, value: str):
        if ' ' in value and not value.startswith('"'):
            value = f'"{value}"'
        property_string = f'{name}={value}\n'

        with open(self.path, 'r') as f:
            lines = f.readlines()

        property_lines = [line_number for line_number, l in enumerate(lines)
                          if l.startswith(name)]
        if len(property_lines) > 1:
            raise Exception(
                f'Multiple occurrences of {name} in {self.path}')
        elif len(property_lines) == 1:
            property_line = property_lines[0]
            lines[property_line] = property_string
        else:
            lines.append(property_string)

        with open(self.path, 'w') as f:
            f.writelines(lines)
