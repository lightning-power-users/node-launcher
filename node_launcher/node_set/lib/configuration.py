from typing import List, Optional

from node_launcher.gui.qt import Signal, QObject
from node_launcher.node_set.lib.configuration_file import ConfigurationFile
from node_launcher.node_set.lib.configuration_property import ConfigurationProperty


class Configuration(QObject):

    configuration_changed = Signal(ConfigurationProperty, ConfigurationProperty)

    def __init__(self, name: str, path: str, assign_op: str = '=', keys_info=None):
        super().__init__()

        self._name = name
        self._file = ConfigurationFile(path=path, assign_op=assign_op)
        self._configurations: List[ConfigurationProperty] = []
        self._keys_info = keys_info or {}

        self._last_identifier = 0

        self._save_disabled = False

    @property
    def file(self):
        return self._file

    # Internal

    def _generate_identifier(self) -> str:
        self._last_identifier += 1
        return '_new_' + str(self._last_identifier)

    def _is_valid_configuration(self, name: str, value: str, default=True) -> bool:
        key_info = self._keys_info.get(name)
        if key_info is None:
            return default
        else:
            validators = key_info.get('validators')
            if not validators:
                return True
            return all([validator(value) for validator in validators])

    # File Management

    def load(self):
        self._save_disabled = True
        self._configurations = []
        for identifier, name, value in self._file.read():
            self.append_configuration(name, value, identifier)
        self._save_disabled = False

    def save(self):
        if not self._save_disabled:
            self.file.save(self._configurations)

    # Get

    def __contains__(self, item):
        for configuration in self._configurations:
            if configuration.name == item:
                return True

        return False

    def __getitem__(self, item):
        configurations = self.get_configurations_by_name(item)
        return configurations[0].value if configurations else None

    def get_all_configurations(self) -> List[ConfigurationProperty]:
        configurations = []
        for configuration in self._configurations:
            configurations.append(configuration.copy())

        return configurations

    def get_configurations_by_name(self, name: str) -> List[ConfigurationProperty]:
        configurations = []
        for configuration in self._configurations:
            if configuration.name == name:
                configurations.append(configuration.copy())

        return configurations

    def get_configuration_by_identifier(self, identifier: str) -> Optional[ConfigurationProperty]:
        for conf in self._configurations:
            if conf.identifier == identifier:
                return conf.copy()

        return None

    # Remove

    def __delitem__(self, key):
        return self.remove_configuration_by_name(key)

    def remove_configuration_by_name(self, name: str, signal: bool = True) -> List[ConfigurationProperty]:
        new_configurations: List[ConfigurationProperty] = []
        removed_configurations = []
        for configuration in self._configurations:
            if configuration.name != name:
                new_configurations.append(configuration)
            else:
                removed_configurations.append(configuration)

        self._configurations = new_configurations

        if signal:
            for configuration in removed_configurations:
                self.configuration_changed.emit(configuration, None)

        self.save()

        return removed_configurations

    def remove_configuration_by_identifier(self, identifier: str, signal: bool = True) -> Optional[ConfigurationProperty]:
        new_configurations: List[ConfigurationProperty] = []
        removed_configuration: ConfigurationProperty = None
        for configuration in self._configurations:
            if configuration.identifier != identifier:
                new_configurations.append(configuration)
            else:
                removed_configuration = configuration

        self._configurations = new_configurations

        if signal and removed_configuration:
            self.configuration_changed.emit(removed_configuration, None)

        self.save()

        return removed_configuration

    # Add / Modify

    def __setitem__(self, key, value):
        if isinstance(value, list):
            self.remove_configuration_by_name(key)
            added_configurations = []
            for val in value:
                added_configuration = self.append_configuration(key, val)
                if added_configuration is not None:
                    added_configurations.append(added_configuration)
            return added_configurations
        else:
            return self.replace_configuration(key, value)

    def set_default_configuration(self, name: str, value, signal: bool = True) -> List[ConfigurationProperty]:
        existing_configurations = self.get_configurations_by_name(name)

        if not existing_configurations:
            added_configuration = self.append_configuration(name, value)
            if added_configuration is not None:

                if signal:
                    self.configuration_changed.emit(added_configuration, added_configuration)

                self.save()

                return [added_configuration]

        return existing_configurations

    def edit_configuration(self, identifier: str, value, signal: bool = True) -> Optional[ConfigurationProperty]:
        for configuration in self._configurations:
            if configuration.identifier == identifier:

                if not self._is_valid_configuration(configuration.name, value):
                    return None

                old_configuration = configuration.copy()
                configuration.value = value

                if signal:
                    self.configuration_changed.emit(old_configuration, configuration)

                self.save()

                return configuration

        return None

    def replace_configuration(self, name: str, value, signal: bool = True) -> Optional[ConfigurationProperty]:

        removed_configurations = self.remove_configuration_by_name(name, signal=False)

        identifier = None
        if len(removed_configurations) > 0:
            identifier = removed_configurations[0].identifier

        added_configuration = self.append_configuration(name, value, identifier, signal=False)

        if added_configuration is not None:
            if signal:
                for i in range(len(removed_configurations)):
                    if i == 0:
                        self.configuration_changed.emit(removed_configurations[0], added_configuration)
                    else:
                        self.configuration_changed.emit(removed_configurations[i], None)
        else:
            for configuration in removed_configurations:
                self.append_configuration(configuration.name, configuration.value, configuration.identifier, False)

        self.save()

        return added_configuration

    def append_configuration(self, name: str, value, identifier=None, signal: bool = True) -> Optional[ConfigurationProperty]:

        if isinstance(value, bool):
            value = 1 if value else 0

        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                pass

        if not self._is_valid_configuration(name, value):
            return None

        if identifier is None:
            identifier = self._generate_identifier()

        configuration = ConfigurationProperty(identifier, name, value)
        self._configurations.append(configuration)

        # if signal:
        #     self.configuration_changed.emit(None, configuration)

        self.save()

        return configuration
