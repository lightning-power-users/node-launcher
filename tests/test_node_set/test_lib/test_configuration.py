from tempfile import NamedTemporaryFile

import pytest

from node_launcher.node_set.lib.configuration import Configuration
from node_launcher.node_set.lib.configuration_property import ConfigurationProperty


@pytest.fixture
def configuration():
    with NamedTemporaryFile(suffix='.conf', delete=True) as f:
        name = f.name
    configuration = Configuration('test_node', name)
    configuration.load()
    return configuration


test_value = 'test_value'


class TestConfiguration(object):
    def test_file_save(self, configuration: Configuration):
        configuration['test_attribute'] = test_value
        with open(configuration.file.path, 'r') as f:
            text = f.read()
            assert f'test_attribute={test_value}' in text

    def test_file_save_bool(self, configuration: Configuration):
        configuration['test_bool'] = True
        with open(configuration.file.path, 'r') as f:
            text = f.read()
            assert f'test_bool=1' in text

    def test_setitem_getitem(self, configuration: Configuration):
        configuration['test_attribute'] = test_value
        assert configuration['test_attribute'] == test_value

    def test_setitem_getitem_bool(self, configuration: Configuration):
        configuration['test_bool_false'] = False
        configuration['test_bool_true'] = True
        assert configuration['test_bool_false'] == False
        assert configuration['test_bool_true'] == True

    def test_delitem(self, configuration: Configuration):
        configuration['test_attribute'] = test_value
        assert configuration['test_attribute'] == test_value
        del configuration['test_attribute']
        assert configuration['test_attribute'] is None

    def test_contains(self, configuration: Configuration):
        configuration['test_attribute'] = test_value
        assert 'test_attribute' in configuration
        assert 'abc' not in configuration

    def test_get_all_configurations(self, configuration: Configuration):
        configuration['a'] = 'a'
        configuration['b'] = 1
        configuration['c'] = False

        assert configuration.get_all_configurations() == [
            ConfigurationProperty('_new_1', 'a', 'a'),
            ConfigurationProperty('_new_2', 'b', 1),
            ConfigurationProperty('_new_3', 'c', False)
        ]

    def test_get_configurations_by_name(self, configuration: Configuration):
        configuration['a'] = ['a', 1]
        configuration['b'] = False

        assert configuration.get_configurations_by_name('a') == [
            ConfigurationProperty('_new_1', 'a', 'a'),
            ConfigurationProperty('_new_2', 'a', 1)
        ]

    def test_get_configuration_by_identifier(self, configuration: Configuration):
        configuration['a'] = ['a', 1]
        configuration['b'] = False

        assert configuration.get_configuration_by_identifier('_new_3') == ConfigurationProperty('_new_3', 'b', False)

    def test_remove_configuration_by_name(self, configuration: Configuration):
        configuration['a'] = ['a', 1]
        configuration['b'] = False

        configuration.remove_configuration_by_name('a')
        assert configuration['a'] is None
        assert not configuration['b']

    def test_remove_configuration_by_identifier(self, configuration: Configuration):
        configuration['a'] = ['a', 1]
        configuration['b'] = False

        configuration.remove_configuration_by_identifier('_new_1')
        assert configuration.get_all_configurations() == [
            ConfigurationProperty('_new_2', 'a', 1),
            ConfigurationProperty('_new_3', 'b', False)
        ]

    def test_set_default_configuration(self, configuration: Configuration):
        configuration.set_default_configuration('a', 1)
        assert configuration['a'] == 1
        configuration.set_default_configuration('a', 2)
        assert configuration['a'] == 1

    def test_edit_configuration(self, configuration: Configuration):
        configuration['a'] = ['a', 1]
        configuration['b'] = False

        configuration.edit_configuration('_new_2', 2)

        assert configuration.get_all_configurations() == [
            ConfigurationProperty('_new_1', 'a', 'a'),
            ConfigurationProperty('_new_2', 'a', 2),
            ConfigurationProperty('_new_3', 'b', False)
        ]

    def test_replace_configuration(self, configuration: Configuration):
        configuration['a'] = ['a', 1]
        configuration['b'] = False

        configuration.replace_configuration('a', 5)

        all_configurations = configuration.get_all_configurations()

        assert ConfigurationProperty('_new_1', 'a', 5) in all_configurations and \
            ConfigurationProperty('_new_3', 'b', False) in all_configurations

    def test_append_configuration(self, configuration: Configuration):
        configuration.append_configuration('a', 1)

        assert configuration.get_all_configurations() == [
            ConfigurationProperty('_new_1', 'a', 1)
        ]

        configuration.append_configuration('a', 2)

        assert configuration.get_all_configurations() == [
            ConfigurationProperty('_new_1', 'a', 1),
            ConfigurationProperty('_new_2', 'a', 2)
        ]
