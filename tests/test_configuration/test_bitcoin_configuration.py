import os
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest

from node_launcher.configuration.bitcoin_configuration import (
    BitcoinConfiguration
)
from node_launcher.configuration.configuration_file import ConfigurationFile
from node_launcher.constants import (
    BITCOIN_DATA_PATH,
    OPERATING_SYSTEM
)


@pytest.fixture
def bitcoin_configuration():
    with NamedTemporaryFile(suffix='-bitcoin.conf', delete=False) as f:
        bitcoin_configuration = BitcoinConfiguration(network='testnet',
                                                     configuration_path=f.name)
    return bitcoin_configuration


class TestBitcoinConfiguration(object):
    @staticmethod
    def test_configuration_path_no_directory():
        with TemporaryDirectory() as tmpdirname:
            os.rmdir(tmpdirname)
            configuration_path = os.path.join(tmpdirname, 'bitcoin.conf')
            bitcoin_configuration = BitcoinConfiguration(network='testnet',
                                                         configuration_path=configuration_path)
            assert os.path.isfile(bitcoin_configuration.file.path)

    @staticmethod
    def test_configuration_path(bitcoin_configuration: BitcoinConfiguration):
        assert bitcoin_configuration.file.path.endswith('bitcoin.conf')
        assert os.path.isfile(bitcoin_configuration.file.path)

    @staticmethod
    def test_datadir(bitcoin_configuration: BitcoinConfiguration):
        assert bitcoin_configuration.file.datadir == BITCOIN_DATA_PATH[
            OPERATING_SYSTEM]
        assert os.path.exists(bitcoin_configuration.file.datadir)

    @staticmethod
    def test_prune(bitcoin_configuration: BitcoinConfiguration):
        datadir = bitcoin_configuration.file.datadir
        should_prune = bitcoin_configuration.hard_drives.should_prune(datadir,
                                                                      True)
        assert bitcoin_configuration.file.prune == should_prune

    @staticmethod
    def test_set_prune(bitcoin_configuration: BitcoinConfiguration):
        bitcoin_configuration.set_prune(True)
        pruned = ConfigurationFile(bitcoin_configuration.file.path)
        assert pruned.prune
        assert not pruned.txindex
        bitcoin_configuration.set_prune(False)
        unpruned = ConfigurationFile(bitcoin_configuration.file.path)
        assert not unpruned.prune
        assert unpruned.txindex

    @staticmethod
    def test_rpcuser(bitcoin_configuration: BitcoinConfiguration):
        assert bitcoin_configuration.file.rpcuser

    @staticmethod
    def test_set_rpcuser(bitcoin_configuration: BitcoinConfiguration):
        bitcoin_configuration.file.rpcuser = 'test_user'
        changed = ConfigurationFile(bitcoin_configuration.file.path)
        assert changed.rpcuser == 'test_user'
        bitcoin_configuration.file.rpcuser = 'test_user_2'
        changed_again = ConfigurationFile(bitcoin_configuration.file.path)
        assert changed_again.rpcuser == 'test_user_2'

    @staticmethod
    def test_autoconfigure_datadir(bitcoin_configuration: BitcoinConfiguration):
        datadir = bitcoin_configuration.file.datadir
        prune = bitcoin_configuration.file.prune
        txindex = bitcoin_configuration.file.txindex
        assert datadir
        assert prune != txindex

    def test_detect_zmq_ports(self,
                              bitcoin_configuration: BitcoinConfiguration):
        result = bitcoin_configuration.detect_zmq_ports()
        assert bitcoin_configuration.zmq_block_port < bitcoin_configuration.zmq_tx_port
        assert isinstance(result, bool)
