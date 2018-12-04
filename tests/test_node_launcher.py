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
def mocked_node_launcher(mock_command_generator):
    launch_fn = MagicMock()
    launch_terminal_fn = MagicMock()
    mocked_node_launcher = NodeLauncher(mock_command_generator,
                                        launch_fn,
                                        launch_terminal_fn)
    return mocked_node_launcher


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
    assert result


class TestNodeLauncherUnitTests(object):
    def test_testnet_bitcoin_qt_node(self, mocked_node_launcher: NodeLauncher):
        mocked_node_launcher.testnet_bitcoin_qt_node()
        mocked_node_launcher.command_generator.testnet_bitcoin_qt.assert_called_once()

    def test_mainnet_bitcoin_qt_node(self, mocked_node_launcher: NodeLauncher):
        mocked_node_launcher.mainnet_bitcoin_qt_node()
        mocked_node_launcher.command_generator.mainnet_bitcoin_qt.assert_called_once()

    def test_testnet_lnd_node(self, mocked_node_launcher: NodeLauncher):
        mocked_node_launcher.testnet_lnd_node()
        mocked_node_launcher.command_generator.testnet_lnd.assert_called_once()

    def test_mainnet_lnd_node(self, mocked_node_launcher: NodeLauncher):
        mocked_node_launcher.mainnet_lnd_node()
        mocked_node_launcher.command_generator.mainnet_lnd.assert_called_once()
