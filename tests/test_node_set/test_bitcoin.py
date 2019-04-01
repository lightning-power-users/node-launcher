import os
from tempfile import TemporaryDirectory

from node_launcher.constants import (
    MAINNET_PRUNE,
    TESTNET_PRUNE
)
from node_launcher.node_set.bitcoin import Bitcoin
from node_launcher.services.configuration_file import ConfigurationFile


class TestBitcoinConfiguration(object):
    @staticmethod
    def test_configuration_path_no_directory():
        with TemporaryDirectory() as tmpdirname:
            os.rmdir(tmpdirname)
            configuration_path = os.path.join(tmpdirname, 'bitcoin.conf')
            bitcoin = Bitcoin(configuration_file_path=configuration_path)
            assert os.path.isfile(bitcoin.file.path)

    @staticmethod
    def test_configuration_path(bitcoin: Bitcoin):
        assert bitcoin.file.path.endswith('bitcoin.conf')
        assert os.path.isfile(bitcoin.file.path)

    @staticmethod
    def test_datadir(bitcoin: Bitcoin):
        assert os.path.exists(bitcoin.file['datadir'])
        assert 'bitcoin.conf' in os.listdir(bitcoin.file['datadir'])

    @staticmethod
    def test_prune(bitcoin: Bitcoin):
        assert (
                bitcoin.file['prune'] == TESTNET_PRUNE
                or bitcoin.file['prune'] == 0
                or bitcoin.file['prune'] == MAINNET_PRUNE
        )

    @staticmethod
    def test_set_prune(bitcoin: Bitcoin):
        bitcoin.set_prune(True)
        pruned = ConfigurationFile(bitcoin.file.path)
        assert pruned['prune']
        assert not pruned['txindex']
        bitcoin.set_prune(False)
        unpruned = ConfigurationFile(bitcoin.file.path)
        assert not unpruned['prune']
        assert unpruned['txindex']

    @staticmethod
    def test_rpcuser(bitcoin: Bitcoin):
        assert bitcoin.file['rpcuser']

    @staticmethod
    def test_set_rpcuser(bitcoin: Bitcoin):
        bitcoin.file['rpcuser'] = 'test_user'
        changed = ConfigurationFile(bitcoin.file.path)
        assert changed['rpcuser'] == 'test_user'
        bitcoin.file['rpcuser'] = 'test_user_2'
        changed_again = ConfigurationFile(bitcoin.file.path)
        assert changed_again['rpcuser'] == 'test_user_2'

    @staticmethod
    def test_autoconfigure_datadir(bitcoin: Bitcoin):
        datadir = bitcoin.file['datadir']
        prune = bitcoin.file['prune']
        txindex = bitcoin.file['txindex']
        assert datadir
        assert prune != txindex

    def test_file_changed(self, bitcoin: Bitcoin):
        bitcoin.file['rpcport'] = 8338
        bitcoin.config_file_changed()
        new_config = bitcoin.file.snapshot
        bitcoin.running = False
        assert bitcoin.rpc_port == new_config['rpcport'] == new_config['main.rpcport'] == 8338
        assert bitcoin.restart_required == False
        bitcoin.running = True
        assert bitcoin.restart_required == True
        bitcoin.file['port'] = 8336
        bitcoin.config_file_changed()
        new_config = bitcoin.file.snapshot
        bitcoin.running = False
        assert bitcoin.node_port == new_config['port'] == new_config['main.port'] == 8336
        assert bitcoin.restart_required == False
        bitcoin.running = True
        assert bitcoin.restart_required == True

