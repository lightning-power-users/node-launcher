from typing import Any, List

from PySide2.QtCore import Signal, QObject

from node_launcher.node_set.lib.configuration_cache import ConfigurationCache
from node_launcher.node_set.lib.configuration_file import ConfigurationFile


class Configuration(QObject):

    parameter_change = Signal(str, str, list)

    def __init__(self, name: str, path: str, assign_op: str = '='):
        super().__init__()
        self.name = name
        self.file = ConfigurationFile(path=path, assign_op=assign_op)
        self.cache = ConfigurationCache()
        self.lines = None

    def __getitem__(self, name):
        return self.cache[name]

    def __setitem__(self, key: str, new_value: Any) -> None:
        if not isinstance(new_value, list):
            new_value = [new_value]
        self.cache[key] = new_value

        string_values = self.stringify_values(new_value)
        self.lines = self.file.update(key, string_values)
        self.parameter_change.emit(self.name, key, string_values)

    @staticmethod
    def stringify_values(new_values: List[Any]) -> List[str]:
        new_list = []
        for new_value in new_values:
            if isinstance(new_value, str):
                new_value = [new_value]
            elif isinstance(new_value, bool):
                new_value = [str(int(new_value))]
            elif isinstance(new_value, int):
                new_value = [str(new_value)]
            elif new_value is None:
                pass
            else:
                raise NotImplementedError(f'list_string_value for {type(new_value)}')
            new_list.append(new_value)
        return new_values

    def load(self):
        self.lines = self.file.read()
        for key, value in self.lines:
            self.cache[key] = value
            self.parameter_change.emit(self.name, key, value)
