import os
from os.path import isfile
from tempfile import NamedTemporaryFile

import pytest

from node_launcher.node_set.lib.configuration_file import ConfigurationFile
from node_launcher.node_set.lib.configuration_property import ConfigurationProperty


@pytest.fixture
def configuration_file():
    with NamedTemporaryFile(suffix='.conf', delete=True) as f:
        name = f.name
    configuration_file = ConfigurationFile(name)
    configuration_file.read()
    return configuration_file


class TestConfigurationFile(object):
    def test_path(self, configuration_file: ConfigurationFile):
        assert isfile(configuration_file.path)

    def test_parse_line(self, configuration_file: ConfigurationFile):
        test_vars = [
            ['# comment', '', ''],
            ['key=value', 'key', 'value'],
            ['key = value', 'key', 'value'],
            [' key = value ', 'key', 'value'],
            ['=value', '', ''],
            ['key=', '', ''],
            ['', '', '']
        ]

        for test_var in test_vars:
            key, value = configuration_file.parse_line(test_var[0])
            print(key)
            print(value)
            assert key == test_var[1] and value == test_var[2]

    def test_read(self, configuration_file: ConfigurationFile):
        configuration: ConfigurationProperty = ConfigurationProperty('1', 'key', 'value')
        configuration_file.save([configuration])
        lines = configuration_file.read()

        assert len(lines) == 1 and lines[0] == ('0', 'key', 'value')

    def test_save(self, configuration_file: ConfigurationFile):
        test_value = 'test_value'
        configuration: ConfigurationProperty = ConfigurationProperty('1', 'test_key', test_value)
        configuration_file.save([configuration])
        with open(configuration_file.path, 'r') as f:
            text = f.read()
            assert test_value in text

    def test_assign_op(self, configuration_file: ConfigurationFile):
        configuration: ConfigurationProperty = ConfigurationProperty('1', 'key', 'value')
        configuration_file.save([configuration])
        with open(configuration_file.path, 'r') as f:
            text = f.read()
            assert 'key=value' in text
        os.remove(configuration_file.path)
        new_configuration_file = ConfigurationFile(configuration_file.path, ' ')
        new_configuration_file.read()
        new_configuration_file.save([configuration])
        with open(new_configuration_file.path, 'r') as f:
            text = f.read()
            assert 'key=value' not in text
            assert 'key value' in text
