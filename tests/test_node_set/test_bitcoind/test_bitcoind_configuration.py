import os
from tempfile import mkdtemp

import pytest

from node_launcher.node_set.bitcoind.bitcoind_configuration import \
    BitcoindConfiguration
from node_launcher.node_set.lib.configuration_file import ConfigurationFile


@pytest.fixture
def bitcoind_configuration() -> BitcoindConfiguration:
    tmpdirname = mkdtemp()
    os.rmdir(tmpdirname)
    configuration_path = os.path.join(tmpdirname, 'bitcoin.conf')
    conf = BitcoindConfiguration()
    conf.file_path = configuration_path
    conf.load()
    conf.check()
    return conf


# noinspection PyShadowingNames
class TestBitcoinConfiguration(object):
    @staticmethod
    def test_set_prune(bitcoind_configuration: BitcoindConfiguration):
        bitcoind_configuration.set_prune(True)
        pruned = ConfigurationFile(bitcoind_configuration.file.path)
        assert pruned['prune']
        assert not pruned['txindex']
        bitcoind_configuration.set_prune(False)
        unpruned = ConfigurationFile(bitcoind_configuration.file.path)
        assert not unpruned['prune']
        assert unpruned['txindex']

    @staticmethod
    def test_rpcuser(bitcoind_configuration: BitcoindConfiguration):
        assert bitcoind_configuration.file['rpcuser']

    @staticmethod
    def test_set_rpcuser(bitcoind_configuration: BitcoindConfiguration):
        bitcoind_configuration.file['rpcuser'] = 'test_user'
        changed = ConfigurationFile(bitcoind_configuration.file.path)
        assert changed['rpcuser'] == 'test_user'
        bitcoind_configuration.file['rpcuser'] = 'test_user_2'
        changed_again = ConfigurationFile(bitcoind_configuration.file.path)
        assert changed_again['rpcuser'] == 'test_user_2'

    @staticmethod
    def test_autoconfigure_datadir(bitcoind_configuration: BitcoindConfiguration):
        datadir = bitcoind_configuration.file['datadir']
        prune = bitcoind_configuration.file['prune']
        txindex = bitcoind_configuration.file['txindex']
        assert datadir
        assert prune != txindex

    @pytest.mark.skip
    def test_file_changed(self, bitcoind_configuration: BitcoindConfiguration):
        bitcoind_configuration.file['rpcport'] = 8338
        bitcoind_configuration.config_file_changed()
        new_config = bitcoind_configuration.file.snapshot
        bitcoind_configuration.running = False
        assert bitcoind_configuration.rpc_port == new_config['rpcport'] == new_config['main.rpcport'] == 8338
        assert bitcoind_configuration.restart_required == False
        bitcoind_configuration.running = True
        assert bitcoind_configuration.restart_required == True
        bitcoind_configuration.file['port'] = 8336
        bitcoind_configuration.config_file_changed()
        new_config = bitcoind_configuration.file.snapshot
        bitcoind_configuration.running = False
        assert bitcoind_configuration.node_port == new_config['port'] == new_config['main.port'] == 8336
        assert bitcoind_configuration.restart_required == False
        bitcoind_configuration.running = True
        assert bitcoind_configuration.restart_required == True

