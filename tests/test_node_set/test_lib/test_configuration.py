from tempfile import NamedTemporaryFile

import pytest

from node_launcher.node_set.lib.configuration import Configuration


@pytest.fixture
def configuration():
    with NamedTemporaryFile(suffix='.conf', delete=True) as f:
        name = f.name
    configuration = Configuration(name)
    configuration.load()
    return configuration


test_value = 'test_value'


class TestConfiguration(object):
    def test_setattr(self, configuration: Configuration):
        configuration['test_attribute'] = test_value
        with open(configuration.file.path, 'r') as f:
            text = f.read()
            assert test_value in text

    def test_getattr(self, configuration: Configuration):
        configuration['test_attribute'] = test_value
        new_object = Configuration(configuration.file.path)
        new_object.load()
        assert new_object['test_attribute'] == test_value

    def test_setattr_bool(self, configuration: Configuration):
        configuration['test_bool_false'] = False
        configuration['test_bool_true'] = True
        with open(configuration.file.path, 'r') as f:
            text = f.read()
            assert 'test_bool_false=0' in text
            assert 'test_bool_true=1' in text

    def test_getattr_bool(self, configuration: Configuration):
        configuration['test_bool_true'] = True
        configuration['test_bool_false'] = False
        new_object = Configuration(configuration.file.path)
        new_object.load()
        assert new_object['test_bool_true']
        assert not new_object['test_bool_false']
