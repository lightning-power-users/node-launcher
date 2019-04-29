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
        assert len(lnd_configuration['multi_property']) == 2

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

    @pytest.mark.skip
    def test_bitcoin_file_changed(self, lnd: LndConfiguration):
        lnd.bitcoind_node.file['rpcport'] = 8338
        lnd.bitcoind_node.running = False
        lnd.bitcoind_node.config_file_changed()
        lnd.bitcoin_config_file_changed()
        new_config = lnd.file.snapshot
        lnd.running = False
        assert lnd.file['bitcoind.rpchost'] == new_config['bitcoind.rpchost'] == '127.0.0.1:8338'
        assert lnd.restart_required == False
        lnd.bitcoind_node.running = True
        lnd.bitcoind_node.config_snapshot = lnd.bitcoind_node.file.snapshot
        assert lnd.bitcoind_node.config_snapshot['rpcport'] == 8338
        lnd.bitcoind_node.file['rpcport'] = 8340
        lnd.bitcoind_node.config_file_changed()
        lnd.bitcoin_config_file_changed()
        new_config = lnd.file.snapshot
        assert lnd.file['bitcoind.rpchost'] == new_config['bitcoind.rpchost'] == '127.0.0.1:8340'
        assert lnd.restart_required == False
        lnd.running = True
        assert lnd.bitcoind_node.restart_required == True
        assert lnd.restart_required == True

    @pytest.mark.skip
    def test_file_changed(self, lnd: LndConfiguration):
        lnd.file['listen'] = '127.0.0.1:9739'
        lnd.config_file_changed()
        lnd.running = False
        new_config = lnd.file.snapshot
        assert lnd.node_port == new_config['listen'].split(':')[-1] == '9739'
        assert lnd.restart_required == False
        lnd.running = True
        lnd.file['listen'] = '127.0.0.1:9741'
        lnd.config_file_changed()
        new_config = lnd.file.snapshot
        assert lnd.node_port == new_config['listen'].split(':')[-1] == '9741'
