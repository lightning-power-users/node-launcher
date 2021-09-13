import os
from tempfile import mkdtemp

import pytest

from node_launcher.node_set.lnd.lnd_configuration import LndConfiguration
from node_launcher.port_utilities import is_port_in_use


@pytest.fixture
def lnd_configuration() -> LndConfiguration:
    tmpdirname = mkdtemp()
    os.rmdir(tmpdirname)
    configuration_path = os.path.join(tmpdirname, 'lnd.conf')
    conf = LndConfiguration()
    conf.file.path = configuration_path
    conf.load()
    conf.check()
    return conf


class TestDirectoryConfiguration(object):
    def test_lnd_data_path(self, lnd_configuration: LndConfiguration):
        assert os.path.isdir(lnd_configuration.lnddir)

    def test_multi_property(self, lnd_configuration: LndConfiguration):
        lnd_configuration['multi_property'] = [
            'test1',
            'test2'
        ]
        assert len(lnd_configuration.get_configurations_by_name('multi_property')) == 2

    def test_multi_listen(self, lnd_configuration: LndConfiguration):
        lnd_configuration['listen'] = [
            '127.0.0.1:9835',
            '192.168.1.1:9736',
        ]
        assert lnd_configuration.node_port == 9835

    def test_rest(self, lnd_configuration: LndConfiguration):
        assert not is_port_in_use(lnd_configuration.rest_port)

    def test_node(self, lnd_configuration: LndConfiguration):
        assert not is_port_in_use(lnd_configuration.node_port)

    def test_grpc(self, lnd_configuration: LndConfiguration):
        assert not is_port_in_use(lnd_configuration.grpc_port)
