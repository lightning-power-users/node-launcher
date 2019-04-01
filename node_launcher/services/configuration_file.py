import os
from os.path import isfile, isdir, pardir
from typing import List, Any

from node_launcher.constants import NODE_LAUNCHER_RELEASE
from node_launcher.logging import log
from PySide2.QtCore import QFileSystemWatcher


class ConfigurationFile(dict):
    file_watcher: QFileSystemWatcher

    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path
        parent = os.path.abspath(os.path.join(path, pardir))
        if not isdir(parent):
            log.info(
                'Creating directory',
                path=parent
            )
            os.mkdir(parent)
        if not isfile(self.path):
            log.info(
                'Creating file',
                path=self.path
            )
            with open(self.path, 'w') as f:
                f.write('# Auto-Generated Configuration File' + os.linesep + os.linesep)
                f.write(f'# Node Launcher version {NODE_LAUNCHER_RELEASE}' + os.linesep + os.linesep)
                f.flush()

        self.cache = {}
        self.aliases = {
            'rpcport': 'main.rpcport', 'main.rpcport': 'rpcport', 'port': 'main.port', 'main.port': 'port',
            'walletdir': 'main.walletdir', 'main.walletdir': 'walletdir'
        }
        self.populate_cache()
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.addPath(self.path)

    def populate_cache(self):
        with open(self.path, 'r') as f:
            property_lines = f.readlines()
        self.cache = {}
        for property_line in property_lines:
            key_value = property_line.split('=')
            key = key_value[0]
            if not key.strip():
                continue
            value = key_value[1:]
            value = '='.join(value).strip()
            value = value.replace('"', '')
            if len(value) == 1 and value.isdigit():
                value = bool(int(value))
            elif value.isdigit():
                value = int(value)

            existing_value = self.cache.get(key, 'no_key')
            if existing_value == 'no_key':
                self.cache[key] = value
                if key in self.aliases.keys():
                    self.cache[self.aliases[key]] = value
            elif isinstance(existing_value, list):
                self.cache[key].append(value)
                if key in self.aliases.keys():
                    self.cache[self.aliases[key]].append(value)
            else:
                self.cache[key] = [existing_value, value]
                if key in self.aliases.keys():
                    self.cache[self.aliases[key]] = [existing_value, value]

    def __repr__(self):
        return f'ConfigurationFile: {self.path}'

    def __delitem__(self, v) -> None:
        raise NotImplementedError()

    def __len__(self) -> int:
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()

    def __getitem__(self, name):
        if name in self.aliases.keys():
            if self.cache.get(self.aliases[name], None) is not None:
                return self.cache[self.aliases[name]]
            else:
                return self.cache.get(name, None)
        return self.cache.get(name, None)

    def __setitem__(self, name: str, value: Any) -> None:
        self.cache[name] = value
        if name in self.aliases.keys():
            self.cache[self.aliases[name]] = value
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
        property_lines = [line_number for line_number, l in enumerate(lines)
                          if l.startswith(name)]
        for property_line_index in property_lines:
            lines.pop(property_line_index)
        if value_list is not None:
            for value in value_list:
                property_string = f'{name.strip()}={value.strip()}'
                lines.append(property_string)
        with open(self.path, 'w') as f:
            lines = [l + os.linesep for l in lines]
            f.writelines(lines)

    @property
    def directory(self):
        directory_path = os.path.abspath(
            os.path.join(self.path, os.pardir)
        )
        return directory_path

    @property
    def snapshot(self):
        return self.cache.copy()
