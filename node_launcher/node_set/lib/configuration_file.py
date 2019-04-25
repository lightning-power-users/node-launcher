import os
from os.path import isfile, isdir, pardir
from typing import List, Any

from PySide2.QtGui import QStandardItemModel, QStandardItem

from node_launcher.constants import NODE_LAUNCHER_RELEASE
from node_launcher.logging import log
from PySide2.QtCore import QFileSystemWatcher


class ConfigurationFile(dict):
    file_watcher: QFileSystemWatcher

    def __init__(self, path: str, assign_op: str = '=', **kwargs):
        super().__init__(**kwargs)
        self.path = path
        self.name = os.path.basename(self.path)
        self.assign_op = assign_op
        self.cache = {}
        self.model_repository = QStandardItemModel(0, 3)

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
            with open(self.path, 'w') as f:
                f.write(
                    '# Auto-Generated Configuration File' + os.linesep + os.linesep)
                f.write(
                    f'# Node Launcher version {NODE_LAUNCHER_RELEASE}' + os.linesep + os.linesep)
                f.flush()
        self.initialize_cache_and_model_repository()
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.addPath(self.path)

    def initialize_cache_and_model_repository(self):
        self.cache = {}
        with open(self.path, 'r') as f:
            lines = f.readlines()
        self.populate_cache(lines)
        self.populate_model_repository(lines)

    def parse_line(self, line: str):
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
        for line in lines:
            key, value = self.parse_line(line)
            existing_value = self.cache.get(key, 'no_key')
            if existing_value == 'no_key':
                self.cache[key] = value
            elif isinstance(existing_value, list):
                self.cache[key].append(value)
            else:
                self.cache[key] = [existing_value, value]

    def populate_model_repository(self, lines):
        self.model_repository.clear()
        self.model_repository.setRowCount(len(lines))
        for index, property_line in enumerate(lines):
            key, value = self.parse_line(property_line)
            self.populate_row(index, key, value)

    def populate_row(self, row_index, key, value):
        self.model_repository.setItem(row_index, 0, QStandardItem(self.name))
        self.model_repository.setItem(row_index, 1, QStandardItem(key))
        self.model_repository.setItem(row_index, 2, QStandardItem(value))

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

    def write_property(self, name: str, value_list: List[str]):
        with open(self.path, 'r') as f:
            lines = f.readlines()
            lines = [l.strip() for l in lines if l.strip()]
        existing_property_lines = [line_number for line_number, l in
                                   enumerate(lines)
                                   if l.startswith(name)]
        for property_line_index in existing_property_lines:
            lines.pop(property_line_index)
        if value_list is not None:
            for value_index, value in enumerate(value_list):
                property_string = f'{name.strip()}{self.assign_op}{value}'
                if len(existing_property_lines) >= len(existing_property_lines):
                    lines.insert(existing_property_lines[value_index],
                                 property_string)
                else:
                    lines.append(property_string)
        with open(self.path, 'w') as f:
            lines = [l + os.linesep for l in lines]
            f.writelines(lines)
            self.populate_model_repository(lines)

    @property
    def directory(self):
        directory_path = os.path.abspath(
            os.path.join(self.path, os.pardir)
        )
        return directory_path

    @property
    def snapshot(self):
        return self.cache.copy()
