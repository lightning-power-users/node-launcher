from unittest.mock import MagicMock

import pytest

from node_launcher.command_generator import CommandGenerator


@pytest.fixture
def command_generator():
    command_generator = CommandGenerator(MagicMock(), MagicMock())
    return command_generator


class TestCommandGenerator(object):
    def test_testnet_bitcoin_qt(self, command_generator):
        assert len(command_generator.testnet_bitcoin_qt())

    def test_mainnet_bitcoin_qt(self, command_generator):
        assert len(command_generator.mainnet_bitcoin_qt())

    def test_testnet_lnd(self, command_generator):
        assert len(command_generator.testnet_lnd())
