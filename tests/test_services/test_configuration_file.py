from os.path import isfile
from tempfile import NamedTemporaryFile

import pytest

from node_launcher.services.configuration_file import ConfigurationFile


@pytest.fixture
def configuration_file():
    with NamedTemporaryFile(suffix='.conf', delete=True) as f:
        name = f.name
    configuration_file = ConfigurationFile(name)
    return configuration_file


test_value = 'test_value'


class TestConfigurationFile(object):
    def test_path(self, configuration_file: ConfigurationFile):
        assert isfile(configuration_file.path)

    def test_setattr(self, configuration_file: ConfigurationFile):
        configuration_file['test_attribute'] = test_value
        with open(configuration_file.path, 'r') as f:
            text = f.read()
            assert test_value in text

    def test_getattr(self, configuration_file: ConfigurationFile):
        configuration_file['test_attribute'] = test_value
        new_object = ConfigurationFile(configuration_file.path)
        assert new_object['test_attribute'] == test_value

    def test_setattr_bool(self, configuration_file: ConfigurationFile):
        configuration_file['test_bool_false'] = False
        configuration_file['test_bool_true'] = True
        with open(configuration_file.path, 'r') as f:
            text = f.read()
            assert 'test_bool_false=0' in text
            assert 'test_bool_true=1' in text

    def test_getattr_bool(self, configuration_file: ConfigurationFile):
        configuration_file['test_bool_true'] = True
        configuration_file['test_bool_false'] = False
        new_object = ConfigurationFile(configuration_file.path)
        assert new_object['test_bool_true']
        assert not new_object['test_bool_false']

    def test_assign_op(self, configuration_file: ConfigurationFile):
        configuration_file['key'] = 'value'
        new_object = ConfigurationFile(configuration_file.path, ' ')
        with open(new_object.path, 'r') as f:
            text = f.read()
            assert 'key=value' in text
        new_object['key'] = 'value'
        with open(new_object.path, 'r') as f:
            text = f.read()
            assert 'key=value' not in text
            assert 'key value' in text
