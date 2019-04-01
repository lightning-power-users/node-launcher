import os

from node_launcher.node_set.lnd import (
    Lnd
)
from node_launcher.utilities.utilities import is_port_in_use


class TestDirectoryConfiguration(object):
    def test_lnd_data_path(self, lnd: Lnd):
        assert os.path.isdir(lnd.lnddir)

    def test_multi_property(self, lnd: Lnd):
        lnd.file['multi_property'] = [
            'test1',
            'test2'
        ]
        assert len(lnd.file['multi_property']) == 2

    def test_multi_listen(self, lnd: Lnd):
        lnd.file['listen'] = [
            '127.0.0.1:9835',
            '192.168.1.1:9736',
        ]
        assert lnd.node_port == '9835'

    def test_rest(self, lnd: Lnd):
        assert not is_port_in_use(lnd.rest_port)

    def test_node(self, lnd: Lnd):
        assert not is_port_in_use(lnd.node_port)

    def test_grpc(self, lnd: Lnd):
        assert not is_port_in_use(lnd.grpc_port)

    def test_bitcoin_file_changed(self, lnd: Lnd):
        lnd.bitcoin.file['rpcport'] = 8338
        lnd.bitcoin.running = False
        lnd.bitcoin.config_file_changed()
        lnd.bitcoin_config_file_changed()
        new_config = lnd.file.snapshot
        lnd.running = False
        assert lnd.file['bitcoind.rpchost'] == new_config['bitcoind.rpchost'] == '127.0.0.1:8338'
        assert lnd.restart_required == False
        lnd.bitcoin.running = True
        lnd.bitcoin.config_snapshot = lnd.bitcoin.file.snapshot
        assert lnd.bitcoin.config_snapshot['rpcport'] == 8338
        lnd.bitcoin.file['rpcport'] = 8340
        lnd.bitcoin.config_file_changed()
        lnd.bitcoin_config_file_changed()
        new_config = lnd.file.snapshot
        assert lnd.file['bitcoind.rpchost'] == new_config['bitcoind.rpchost'] == '127.0.0.1:8340'
        assert lnd.restart_required == False
        lnd.running = True
        assert lnd.bitcoin.restart_required == True
        assert lnd.restart_required == True

    def test_file_changed(self, lnd: Lnd):
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
