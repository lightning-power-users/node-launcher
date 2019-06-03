
class ConfigurationProperty:

    def __init__(self, identifier: str, name: str, value):
        self.identifier: str = identifier
        self.name: str = name
        self.value = value

    def copy(self) -> 'ConfigurationProperty':
        return ConfigurationProperty(self.identifier, self.name, self.value)

    def __eq__(self, other):
        if not isinstance(other, ConfigurationProperty):
            return False
        return self.identifier == other.identifier and self.name == other.name and self.value == other.value

    def __repr__(self):
        return f'[{self.identifier}] {self.name}: {self.value}'
