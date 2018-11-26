import os
from tempfile import NamedTemporaryFile

import pytest

from node_launcher.configuration.bitcoin_configuration import (
    BitcoinConfiguration
)


@pytest.fixture
def bitcoin_configuration():
    with NamedTemporaryFile(suffix='-bitcoin.conf', delete=False) as f:
        bitcoin_configuration = BitcoinConfiguration(f.name)
    return bitcoin_configuration


class BitcoinConfigurationTests(object):
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
