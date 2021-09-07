import os
from os.path import isfile, isdir, pardir
from pathlib import Path
from typing import List, Tuple

from node_launcher.constants import NODE_LAUNCHER_RELEASE
from node_launcher.app_logging import log
from node_launcher.gui.qt import QFileSystemWatcher, QObject

from node_launcher.node_set.lib.configuration_property import ConfigurationProperty


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
        key = key_value[0].strip()

        if not key:
            return '', ''

        value = key_value[1:]
        value = self.assign_op.join(value).strip()
        value = value.replace('"', '')

        if not value:
            return '', ''

        return key, value

    def read(self) -> List[Tuple[str, str, str]]:
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

        parsed_lines = []
        index = 0
        for line in lines:
            key, value = self.parse_line(line)
            if key:
                parsed_lines.append((str(index), key, value))
                index += 1

        return parsed_lines

    def save(self, configurations: List[ConfigurationProperty]):
        with open(self.path, 'w') as f:
            lines = [f'{c.name}{self.assign_op}{c.value}{os.linesep}' for c in configurations]
            f.writelines(lines)
