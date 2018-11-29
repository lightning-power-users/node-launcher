import os
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest

from node_launcher.configuration.bitcoin_configuration import (
    BitcoinConfiguration
)
from node_launcher.constants import (
    BITCOIN_DATA_PATH,
    OPERATING_SYSTEM
)


@pytest.fixture
def bitcoin_configuration():
    with NamedTemporaryFile(suffix='-bitcoin.conf', delete=False) as f:
        bitcoin_configuration = BitcoinConfiguration(f.name)
    bitcoin_configuration.write_property('test_property', 'test_value')
    return bitcoin_configuration


class TestBitcoinConfiguration(object):
    @staticmethod
    def test_configuration_path_no_directory(bitcoin_configuration: BitcoinConfiguration):
        with TemporaryDirectory() as tmpdirname:
            os.rmdir(tmpdirname)
            bitcoin_configuration.configuration_path = os.path.join(tmpdirname, 'bitcoin.conf')
            assert os.path.isfile(bitcoin_configuration.configuration_path)

    @staticmethod
    def test_configuration_path(bitcoin_configuration: BitcoinConfiguration):
        assert bitcoin_configuration.configuration_path.endswith('bitcoin.conf')
        assert os.path.isfile(bitcoin_configuration.configuration_path)

    @staticmethod
    def test_generate_file(bitcoin_configuration: BitcoinConfiguration):
        with NamedTemporaryFile(suffix='-bitcoin.conf', delete=True) as f:
            bitcoin_configuration.configuration_path = f.name
        assert not os.path.isfile(bitcoin_configuration.configuration_path)
        bitcoin_configuration.generate_file()
        assert os.path.isfile(bitcoin_configuration.configuration_path)
        with open(bitcoin_configuration.configuration_path, 'r') as f:
            lines = f.readlines()
            lines[0].endswith('Node Launcher')

    @staticmethod
    def test_write_property(bitcoin_configuration: BitcoinConfiguration):
        bitcoin_configuration.write_property('test_write_property', 'test_write_value')
        with open(bitcoin_configuration.configuration_path, 'r') as f:
            data = f.read()
            assert 'test_write_property=test_write_value' in data

    @staticmethod
    def test_read_property(bitcoin_configuration: BitcoinConfiguration):
        result = bitcoin_configuration.read_property('test_property')
        assert result == 'test_value'

    @staticmethod
    def test_datadir(bitcoin_configuration: BitcoinConfiguration):
        assert bitcoin_configuration.datadir == BITCOIN_DATA_PATH[
            OPERATING_SYSTEM]
        assert os.path.exists(bitcoin_configuration.datadir)

    @staticmethod
    def test_prune(bitcoin_configuration: BitcoinConfiguration):
        assert bitcoin_configuration.prune == bitcoin_configuration.should_prune()

    @staticmethod
    def test_set_prune(bitcoin_configuration: BitcoinConfiguration):
        bitcoin_configuration.prune = True
        pruned = BitcoinConfiguration(bitcoin_configuration.configuration_path)
        assert pruned.prune
        bitcoin_configuration.prune = False
        unpruned = BitcoinConfiguration(bitcoin_configuration.configuration_path)
        assert not unpruned.prune

    @staticmethod
    def test_rpcuser(bitcoin_configuration: BitcoinConfiguration):
        assert bitcoin_configuration.rpcuser

    @staticmethod
    def test_set_rpcuser(bitcoin_configuration: BitcoinConfiguration):
        bitcoin_configuration.rpcuser = 'test_user'
        changed = BitcoinConfiguration(bitcoin_configuration.configuration_path)
        assert changed.rpcuser == 'test_user'
        bitcoin_configuration.rpcuser = 'test_user_2'
        changed_again = BitcoinConfiguration(bitcoin_configuration.configuration_path)
        assert changed_again.rpcuser == 'test_user_2'
