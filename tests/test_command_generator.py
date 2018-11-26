import pytest

from node_launcher.command_generator import CommandGenerator
from node_launcher.configuration import Configuration
from node_launcher.constants import OPERATING_SYSTEM, DARWIN, BITCOIN_QT_PATH


@pytest.fixture
def command_generator():
    command_generator = CommandGenerator(
        testnet_conf=Configuration('testnet', pruned=True),
        mainnet_conf=Configuration('mainnet', pruned=True)
    )
    return command_generator


class TestCommandGenerator(object):
    def test_should_prune(self, command_generator: CommandGenerator):
        should_prune = command_generator.should_prune()
        assert should_prune in [True, False]

    def test_bitcoin_qt(self, command_generator):
        command = command_generator.bitcoin_qt(command_generator.mainnet)
        if OPERATING_SYSTEM == DARWIN:
            assert command[0] == BITCOIN_QT_PATH[OPERATING_SYSTEM]
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
