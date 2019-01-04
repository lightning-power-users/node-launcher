import os
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

import pytest

from node_launcher.node_set.bitcoin import (
    Bitcoin
)
from node_launcher.services.configuration_file import ConfigurationFile
from node_launcher.constants import (
    BITCOIN_DATA_PATH,
    OPERATING_SYSTEM,
    IS_WINDOWS, TESTNET_PRUNE, TESTNET)


class TestBitcoinConfiguration(object):
    @staticmethod
    def test_configuration_path_no_directory():
        with TemporaryDirectory() as tmpdirname:
            os.rmdir(tmpdirname)
            configuration_path = os.path.join(tmpdirname, 'bitcoin.conf')
            bitcoin = Bitcoin(TESTNET,
                              configuration_file_path=configuration_path)
            assert os.path.isfile(bitcoin.file.path)

    @staticmethod
    def test_configuration_path(bitcoin: Bitcoin):
        assert bitcoin.file.path.endswith('bitcoin.conf')
        assert os.path.isfile(bitcoin.file.path)

    @staticmethod
    def test_datadir(bitcoin: Bitcoin):
        assert bitcoin.file['datadir'] == BITCOIN_DATA_PATH[
            OPERATING_SYSTEM]
        assert os.path.exists(bitcoin.file['datadir'])

    @staticmethod
    def test_prune(bitcoin: Bitcoin):
        assert (bitcoin.file['prune'] == TESTNET_PRUNE or bitcoin.file['prune'] == 0)

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

    def test_detect_zmq_ports(self, bitcoin: Bitcoin):
        result = bitcoin.detect_zmq_ports()
        assert bitcoin.zmq_block_port < bitcoin.zmq_tx_port
        assert isinstance(result, bool)

    @pytest.mark.slow
    def test_launch(self, bitcoin: Bitcoin):
        if IS_WINDOWS:
            command = ['set', 'path']
        else:
            command = ['echo', 'hello']
        bitcoin.bitcoin_qt = MagicMock(return_value=command)
        result = bitcoin.launch()
        assert result.pid
