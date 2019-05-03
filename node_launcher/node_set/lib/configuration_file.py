import os
from os.path import isfile, isdir, pardir
from pathlib import Path
from typing import List, Any, Tuple

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

    def parse_line(self, line: str) -> Tuple[str, str]:
        if line.startswith('#'):
            return '', ''
        key_value = line.split(self.assign_op)
        key = key_value[0]
        if not key.strip():
            return '', ''
        value = key_value[1:]
        value = self.assign_op.join(value).strip()
        value = value.replace('"', '')
        return key, value

    def read(self) -> List[Tuple[str, str]]:
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
        return [l for l in parsed_lines if l[0]]

    def update(self, key: str, new_value: List[Any]) -> List[Tuple[str, str]]:
        lines = self.write_property(key, new_value)
        parsed_lines = [self.parse_line(l) for l in lines if l[0]]
        return parsed_lines

    def write_property(self, key: str, values: List[str]):
        key = key.strip()
        with open(self.path, 'r') as f:
            lines = f.readlines()
            lines = [l.strip() for l in lines if l.strip()]
        existing_lines = [l for l in enumerate(lines)
                          if l[1].split(self.assign_op)[0] == key]
        existing_line_numbers = [l[0] for l in existing_lines]
        for line_index in sorted(existing_line_numbers, reverse=True):
            lines.pop(line_index)
        if values is not None:
            for value_index, value in enumerate(values):
                property_string = f'{key}{self.assign_op}{value}'
                if existing_lines and value_index < len(existing_line_numbers):
                    lines.insert(existing_line_numbers[value_index],
                                 property_string)
                else:
                    lines.append(property_string)
        with open(self.path, 'w') as f:
            lines = [l + os.linesep for l in lines]
            f.writelines(lines)
        return lines
