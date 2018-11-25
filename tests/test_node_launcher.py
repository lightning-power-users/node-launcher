import platform
from unittest.mock import MagicMock

import pytest

from node_launcher.constants import WINDOWS, OPERATING_SYSTEM
from node_launcher.node_launcher import NodeLauncher, launch, launch_terminal


@pytest.fixture
def mock_command_generator():
    command_generator = MagicMock()
    command_generator.testnet_bitcoin_qt = MagicMock(return_value=None)
    command_generator.mainnet_bitcoin_qt = MagicMock(return_value=None)
    command_generator.testnet_lnd = MagicMock(return_value=None)
    command_generator.mainnet_lnd = MagicMock(return_value=None)
    return command_generator


@pytest.fixture
def node_launcher(mock_command_generator):
    launch_fn = MagicMock()
    launch_terminal_fn = MagicMock()
    node_launcher = NodeLauncher(mock_command_generator,
                                 launch_fn,
                                 launch_terminal_fn)
    return node_launcher


def test_launch():
    if OPERATING_SYSTEM == WINDOWS:
        result = launch(['set', 'path'])
    else:
        result = launch(['echo', 'hello'])
    assert result.pid


@pytest.mark.slow
def test_launch_terminal():
    if OPERATING_SYSTEM == WINDOWS:
        result = launch_terminal(['set', 'path'])
    else:
        result = launch_terminal(['echo', 'hello'])
    assert result is None


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

    def test_launchMainnetLndNode(self, node_launcher):
        node_launcher.launchMainnetLndNode()
        node_launcher.command_generator.mainnet_lnd.assert_called_once()
