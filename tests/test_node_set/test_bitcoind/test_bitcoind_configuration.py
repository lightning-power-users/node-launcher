import os
from tempfile import mkdtemp

import pytest

from node_launcher.node_set.bitcoind.bitcoind_configuration import \
    BitcoindConfiguration
from node_launcher.node_set.lib.configuration import Configuration


@pytest.fixture
def bitcoind_configuration() -> BitcoindConfiguration:
    tmpdirname = mkdtemp()
    os.rmdir(tmpdirname)
    configuration_path = os.path.join(tmpdirname, 'bitcoin.conf')
    conf = BitcoindConfiguration()
    conf.file.path = configuration_path
    conf.load()
    conf['datadir'] = tmpdirname
    conf.check()
    return conf


# noinspection PyShadowingNames
class TestBitcoinConfiguration(object):
    @staticmethod
    def test_set_prune(bitcoind_configuration: BitcoindConfiguration):
        bitcoind_configuration.set_prune(True)
        pruned = Configuration('bitcoind', bitcoind_configuration.file.path)
        pruned.load()
        assert pruned['prune']
        assert not pruned['txindex']
        bitcoind_configuration.set_prune(False)
        unpruned = Configuration('bitcoind', bitcoind_configuration.file.path)
        unpruned.load()
        assert not unpruned['prune']
        assert unpruned['txindex']

    @staticmethod
    def test_rpcuser(bitcoind_configuration: BitcoindConfiguration):
        assert bitcoind_configuration['rpcuser']

    @staticmethod
    def test_set_rpcuser(bitcoind_configuration: BitcoindConfiguration):
        bitcoind_configuration['rpcuser'] = 'test_user'
        changed = Configuration('bitcoind', bitcoind_configuration.file.path)
        changed.load()
        assert changed['rpcuser'] == 'test_user'
        bitcoind_configuration['rpcuser'] = 'test_user_2'
        changed_again = Configuration('bitcoind', bitcoind_configuration.file.path)
        changed_again.load()
        assert changed_again['rpcuser'] == 'test_user_2'

    @staticmethod
    def test_autoconfigure_datadir(bitcoind_configuration: BitcoindConfiguration):
        datadir = bitcoind_configuration['datadir']
        prune = bitcoind_configuration['prune']
        txindex = bitcoind_configuration['txindex']
        assert datadir
        assert prune != txindex

    @pytest.mark.skip
    def test_file_changed(self, bitcoind_configuration: BitcoindConfiguration):
        bitcoind_configuration['rpcport'] = 8338
        bitcoind_configuration.config_file_changed()
        new_config = bitcoind_configuration.file.snapshot
        bitcoind_configuration.running = False
        assert bitcoind_configuration.rpc_port == new_config['rpcport'] == new_config['main.rpcport'] == 8338
        assert bitcoind_configuration.restart_required == False
        bitcoind_configuration.running = True
        assert bitcoind_configuration.restart_required == True
        bitcoind_configuration['port'] = 8336
        bitcoind_configuration.config_file_changed()
        new_config = bitcoind_configuration.file.snapshot
        bitcoind_configuration.running = False
        assert bitcoind_configuration.node_port == new_config['port'] == new_config['main.port'] == 8336
        assert bitcoind_configuration.restart_required == False
        bitcoind_configuration.running = True
        assert bitcoind_configuration.restart_required == True

