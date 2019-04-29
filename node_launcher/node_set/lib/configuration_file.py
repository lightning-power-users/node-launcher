import os
from os.path import isfile, isdir, pardir
from pathlib import Path
from typing import List

from node_launcher.constants import NODE_LAUNCHER_RELEASE
from node_launcher.logging import log
from PySide2.QtCore import QFileSystemWatcher, Signal, QObject


class ConfigurationFile(QObject):
    file_watcher: QFileSystemWatcher

    def __init__(self, path: str, assign_op: str = '='):
        super().__init__()
        self.path = path
        self.directory = Path(path).parent
        self.assign_op = assign_op

    def __repr__(self):
        return f'ConfigurationFile: {self.path}'

    def read(self):
        parent = os.path.abspath(os.path.join(self.path, pardir))
        if not isdir(parent):
            log.info(
                'Creating directory',
                path=parent
            )
            os.makedirs(parent)
        if not isfile(self.path):
            log.info(
                'Creating file',
                path=self.path
            )
            lines = [
                '# Auto-Generated Configuration File' + os.linesep + os.linesep,
                f'# Node Launcher version {NODE_LAUNCHER_RELEASE}' + os.linesep + os.linesep
            ]
            with open(self.path, 'w') as f:
                f.writelines(lines)
        with open(self.path, 'r') as f:
            lines = f.readlines()
        parsed_lines = [self.parse_line(l) for l in lines]
        return [l for l in parsed_lines
                if l[0] is not None and l[1] is not None]

    def parse_line(self, line: str):
        if line.startswith('#'):
            return None, None
        key_value = line.split(self.assign_op)
        key = key_value[0]
        if not key.strip():
            return None, None
        value = key_value[1:]
        value = self.assign_op.join(value).strip()
        value = value.replace('"', '')
        if len(value) == 1 and value.isdigit():
            value = bool(int(value))
        elif value.isdigit():
            value = int(value)
        return key, value

    def update(self, key, new_value):
        if isinstance(new_value, str):
            new_value = [new_value]
        elif isinstance(new_value, bool):
            new_value = [str(int(new_value))]
        elif isinstance(new_value, int):
            new_value = [str(new_value)]
        elif isinstance(new_value, List):
            for item in new_value:
                assert isinstance(item, str)
            pass
        elif new_value is None:
            pass
        else:
            raise NotImplementedError(f'setattr for {type(new_value)}')
        self.write_property(key, new_value)

    def write_property(self, property_key: str, property_value_list: List[str]):
        property_key = property_key.strip()
        with open(self.path, 'r') as f:
            lines = f.readlines()
            lines = [l.strip() for l in lines if l.strip()]
        existing_property_lines = [line_number for line_number, l in
                                   enumerate(lines)
                                   if l.startswith(property_key)]
        for property_line_index in existing_property_lines:
            lines.pop(property_line_index)
        if property_value_list is not None:
            for value_index, value in enumerate(property_value_list):
                property_string = f'{property_key}{self.assign_op}{value}'
                if existing_property_lines:
                    lines.insert(existing_property_lines[value_index],
                                 property_string)
                else:
                    lines.append(property_string)
        with open(self.path, 'w') as f:
            self.lines = [l + os.linesep for l in lines]
            f.writelines(self.lines)
