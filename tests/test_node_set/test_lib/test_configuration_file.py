import os
from os.path import isfile
from tempfile import NamedTemporaryFile

import pytest

from node_launcher.node_set.lib.configuration_file import ConfigurationFile


@pytest.fixture
def configuration_file():
    with NamedTemporaryFile(suffix='.conf', delete=True) as f:
        name = f.name
    configuration_file = ConfigurationFile(name)
    configuration_file.read()
    return configuration_file


test_value = 'test_value'


class TestConfigurationFile(object):
    def test_path(self, configuration_file: ConfigurationFile):
        assert isfile(configuration_file.path)

    def test_update(self, configuration_file: ConfigurationFile):
        configuration_file.update('test_attribute', [test_value])
        with open(configuration_file.path, 'r') as f:
            text = f.read()
            assert test_value in text

    def test_assign_op(self, configuration_file: ConfigurationFile):
        configuration_file.update('key', ['value'])
        with open(configuration_file.path, 'r') as f:
            text = f.read()
            assert 'key=value' in text
        os.remove(configuration_file.path)
        new_object = ConfigurationFile(configuration_file.path, ' ')
        new_object.read()
        new_object.update('key', ['value'])
        with open(new_object.path, 'r') as f:
            text = f.read()
            assert 'key=value' not in text
            assert 'key value' in text

    def test_write_property(self, configuration_file: ConfigurationFile):
        pass
