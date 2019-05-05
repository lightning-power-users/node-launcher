from typing import Any, List


class ConfigurationCache(dict):

    def __init__(self):
        super().__init__()

    def __delitem__(self, v) -> None:
        raise NotImplementedError()

    def __len__(self) -> int:
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()

    def __getitem__(self, name):
        return self.get(name, None)

    def __setitem__(self, key: str, new_values: List[Any]) -> None:
        existing_values = self.get(key, 'no_key')
        parsed_values = []
        for new_value in new_values:
            if isinstance(new_value, str):
                if len(new_value) == 1 and new_value.isdigit():
                    new_value = bool(int(new_value))
                elif new_value.isdigit():
                    new_value = int(new_value)
            parsed_values.append(new_value)

        if existing_values == parsed_values:
            return

        if existing_values == 'no_key':
            super(ConfigurationCache, self).__setitem__(key, parsed_values)
        elif isinstance(existing_values, list):
            for parsed_value in parsed_values:
                if parsed_value in existing_values:
                    continue
                self[key].append(parsed_value)
