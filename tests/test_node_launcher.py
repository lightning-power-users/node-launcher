from unittest.mock import MagicMock

import pytest

from node_launcher.node_launcher import NodeLauncher


@pytest.fixture
def mock_command_generator():
    command_generator = MagicMock()
    command_generator.testnet_bitcoin_qt = MagicMock(return_value=None)
    command_generator.mainnet_bitcoin_qt = MagicMock(return_value=None)
    command_generator.testnet_lnd = MagicMock(return_value=None)
    return command_generator


@pytest.fixture
def node_launcher(mock_command_generator):
    launch_function = MagicMock()
    node_launcher = NodeLauncher(mock_command_generator, launch_function)
    return node_launcher


class TestNodeLauncher(object):
    def test_launchTestnetBitcoinQtNode(self, node_launcher):
        node_launcher.launchTestnetBitcoinQtNode()
        node_launcher.command_generator.testnet_bitcoin_qt.assert_called_once()

    def test_launchTestnetLndNode(self, node_launcher):
        node_launcher.launchTestnetLndNode()
        node_launcher.command_generator.testnet_lnd.assert_called_once()

    def test_launchMainnetBitcoinQtNode(self, node_launcher):
        node_launcher.launchMainnetBitcoinQtNode()
        node_launcher.command_generator.mainnet_bitcoin_qt.assert_called_once()
