import os
from os.path import isfile, isdir, pardir
from typing import List, Any

from node_launcher.constants import NODE_LAUNCHER_RELEASE


class ConfigurationFile(dict):
    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path
        parent = os.path.abspath(os.path.join(path, pardir))
        if not isdir(parent):
            os.mkdir(parent)
        if not isfile(self.path):
            with open(self.path, 'w') as f:
                f.write('# Auto-Generated Configuration File\n\n')
                f.write(f'# Node Launcher version {NODE_LAUNCHER_RELEASE}\n\n')
                f.flush()

    def __delitem__(self, v) -> None:
        raise NotImplementedError()

    def __len__(self) -> int:
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()

    def __getitem__(self, name):
        with open(self.path, 'r') as f:
            lines = f.readlines()
        property_lines = [l for l in lines if l.startswith(name)]
        values = []
        for property_line in property_lines:
            value = property_line.split('=')[1:]
            value = '='.join(value).strip()
            value = value.replace('"', '')
            if len(value) == 1 and value.isdigit():
                value = bool(int(value))
            elif value.isdigit():
                value = int(value)
            values.append(value)

        if not values:
            return None
        elif len(values) == 1:
            return values[0]
        return values

    def __setitem__(self, name: str, value: Any) -> None:
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
        else:
            raise NotImplementedError(f'setattr for {type(value)}')

        self.write_property(name, value)

    def write_property(self, name: str, value_list: List[str]):
        with open(self.path, 'r') as f:
            lines = f.readlines()
        property_lines = [line_number for line_number, l in enumerate(lines)
                          if l.startswith(name)]
        for property_line_index in property_lines:
            lines.pop(property_line_index)
        for value in value_list:
            property_string = f'{name}={value}\n'
            lines.append(property_string)
        with open(self.path, 'w') as f:
            f.writelines(lines)

    @property
    def directory(self):
        directory_path = os.path.abspath(
            os.path.join(self.path, os.pardir)
        )
        return directory_path
