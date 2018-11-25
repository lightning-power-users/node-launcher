import pytest

from node_launcher.command_generator import CommandGenerator
from node_launcher.configuration import Configuration
from node_launcher.constants import OPERATING_SYSTEM, DARWIN


@pytest.fixture
def command_generator():
    command_generator = CommandGenerator(
        testnet_conf=Configuration('testnet', pruned=True),
        mainnet_conf=Configuration('mainnet', pruned=True)
    )
    return command_generator


class TestCommandGenerator(object):
    def test_bitcoin_qt(self, command_generator):
        command = command_generator.bitcoin_qt(command_generator.mainnet)
        if OPERATING_SYSTEM == DARWIN:
            assert command[0] == '/Applications/Bitcoin-Qt.app/Contents/MacOS/Bitcoin-Qt'
            assert command[1].startswith('-datadir=/')

    def test_testnet_bitcoin_qt(self, command_generator):
        command = command_generator.testnet_bitcoin_qt()
        assert command[-1] == '-testnet=1'

    def test_mainnet_bitcoin_qt(self, command_generator):
        command = command_generator.mainnet_bitcoin_qt()
        assert command[-1] == '-testnet=0'

    def test_testnet_lnd(self, command_generator):
        assert len(command_generator.testnet_lnd())

    def test_mainnet_lnd(self, command_generator):
        assert len(command_generator.mainnet_lnd())
