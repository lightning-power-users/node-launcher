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
        if self.cache[name] is not None and len(self.cache[name]) == 1:
            return self.cache[name][0]
        return self.cache[name]

    def __setitem__(self, key: str, new_value: Any) -> None:
        if not isinstance(new_value, list):
            new_value = [new_value]
        self.cache[key] = new_value

        string_values = self.stringify_values(new_value)
        self.lines = self.file.update(key, string_values)
        self.parameter_change.emit(self.name, key, string_values)

    @staticmethod
    def value_to_string(input_value: Any) -> str:
        if isinstance(input_value, str):
            string_value = input_value
        elif isinstance(input_value, bool):
            integer_value = int(input_value)
            string_value = str(integer_value)
        elif isinstance(input_value, int):
            string_value = str(input_value)
        else:
            raise NotImplementedError(f'value_to_string for {type(input_value)}')
        return string_value

    def stringify_values(self, new_values: List[Any]) -> List[str]:
        new_list = [self.value_to_string(iv) for iv in new_values]
        return new_list

    def load(self):
        self.lines = self.file.read()
        for key, value in self.lines:
            self[key] = value
