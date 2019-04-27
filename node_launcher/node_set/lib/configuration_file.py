import os
from os.path import isfile, isdir, pardir
from typing import List, Any

from node_launcher.constants import NODE_LAUNCHER_RELEASE
from node_launcher.logging import log
from PySide2.QtCore import QFileSystemWatcher, Signal, QObject


class ConfigurationFile(QObject):
    file_watcher: QFileSystemWatcher

    line_change = Signal(int, str, str, str)

    def __init__(self, path: str, assign_op: str = '=', **kwargs):
        super().__init__(**kwargs)
        self.path = path
        self.name = os.path.basename(self.path)
        self.assign_op = assign_op
        self.cache = {}
        self.lines = None

    def load(self):
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
            self.lines = [
                '# Auto-Generated Configuration File' + os.linesep + os.linesep,
                f'# Node Launcher version {NODE_LAUNCHER_RELEASE}' + os.linesep + os.linesep
            ]
            with open(self.path, 'w') as f:
                f.writelines(self.lines)
                f.flush()
        self.initialize_cache()

    def initialize_model_repository(self):
        for line_index, line in enumerate(self.lines):
            key, value = self.parse_line(line)
            if key is not None and value is not None:
                self.line_change.emit(line_index, self.name, key, str(value))

    def initialize_cache(self):
        self.cache = {}
        with open(self.path, 'r') as f:
            self.lines = f.readlines()
        self.populate_cache(self.lines)

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

    def populate_cache(self, lines):
        for line_index, line in enumerate(lines):
            key, value = self.parse_line(line)
            existing_value = self.cache.get(key, 'no_key')
            if existing_value == 'no_key':
                self.cache[key] = value
            elif isinstance(existing_value, list):
                self.cache[key].append(value)
            else:
                self.cache[key] = [existing_value, value]

    def __repr__(self):
        return f'ConfigurationFile: {self.path}'

    def __delitem__(self, v) -> None:
        raise NotImplementedError()

    def __len__(self) -> int:
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()

    def __getitem__(self, name):
        return self.cache.get(name, None)

    def __setitem__(self, name: str, value: Any) -> None:
        self.cache[name] = value
        if isinstance(value, str):
            value = [value]
        elif isinstance(value, bool):
            value = [str(int(value))]
        elif isinstance(value, int):
            value = [str(value)]
        elif isinstance(value, List):
            for item in value:
                assert isinstance(item, str)
            pass
        elif value is None:
            pass
        else:
            raise NotImplementedError(f'setattr for {type(value)}')

        self.write_property(name, value)

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
                if len(existing_property_lines) >= len(existing_property_lines):
                    lines.insert(existing_property_lines[value_index],
                                 property_string)
                else:
                    lines.append(property_string)
        with open(self.path, 'w') as f:
            self.lines = [l + os.linesep for l in lines]
            f.writelines(self.lines)

    @property
    def directory(self):
        directory_path = os.path.abspath(
            os.path.join(self.path, os.pardir)
        )
        return directory_path

    @property
    def snapshot(self):
        return self.cache.copy()
