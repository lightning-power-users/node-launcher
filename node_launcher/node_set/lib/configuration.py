import os
from typing import Any

from PySide2.QtCore import Signal, QObject

from node_launcher.node_set.lib.configuration_cache import ConfigurationCache
from node_launcher.node_set.lib.configuration_file import ConfigurationFile


class Configuration(QObject):

    line_change = Signal(str, str, str)

    def __init__(self, name: str, path: str, assign_op: str = '='):
        super().__init__()
        self.name = name
        self.file = ConfigurationFile(path=path, assign_op=assign_op)
        self.cache = None
        self.lines = None

    def __getitem__(self, name):
        return self.cache[name]

    def __setitem__(self, key: str, new_value: Any) -> None:
        old_value = self.cache[key]
        if str(new_value) != str(old_value):
            self.cache[key] = new_value
            self.lines = self.file.update(key, new_value)
            self.line_change.emit(self.name, key, new_value)

    def load(self):
        self.cache = ConfigurationCache()
        self.lines = self.file.read()
        for key, value in self.lines:
            self.cache[key] = value
            self.line_change.emit(self.name, key, value)
