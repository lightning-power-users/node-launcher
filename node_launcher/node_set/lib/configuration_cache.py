from typing import Any


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

    def __setitem__(self, key: str, new_value: Any) -> None:
        existing_value = self.get(key, 'no_key')
        if existing_value == new_value:
            return
        if existing_value == 'no_key':
            super(ConfigurationCache, self).__setitem__(key, new_value)
        elif isinstance(existing_value, list):
            if new_value in existing_value:
                return
            self[key].append(new_value)
        else:
            super(ConfigurationCache, self).__setitem__(key, [existing_value,
                                                              new_value])
