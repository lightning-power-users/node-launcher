from unittest.mock import MagicMock

import pytest
from PySide2.QtCore import Qt

from node_launcher.gui.launch_widget import LaunchWidget


@pytest.fixture
def mock_node_launcher():
    node_launcher = MagicMock()
    node_launcher.launchTestnetBitcoinQtNode = MagicMock(return_value=None)
    node_launcher.launchMainnetBitcoinQtNode = MagicMock(return_value=None)
    node_launcher.launchTestnetLndNode = MagicMock(return_value=None)
    node_launcher.launchMainnetLndNode = MagicMock(return_value=None)
    return node_launcher


@pytest.fixture
def launch_widget(mock_node_launcher):
    launch_widget = LaunchWidget(mock_node_launcher)
    return launch_widget


class TestGui(object):
    def test_launchTestnetBitcoinQtNodeButton(self, qtbot, launch_widget):
        qtbot.mouseClick(launch_widget.launchTestnetBitcoinQtNodeButton,
                         Qt.LeftButton)
        launch_widget.node_launcher.launchTestnetBitcoinQtNode.assert_called_once()

    def test_launchMainnetBitcoinQtNodeButton(self, qtbot, launch_widget):
        qtbot.mouseClick(launch_widget.launchMainnetBitcoinQtNodeButton,
                         Qt.LeftButton)
        launch_widget.node_launcher.launchMainnetBitcoinQtNode.assert_called_once()

    def test_launchTestnetLndNodeButton(self, qtbot, launch_widget):
        qtbot.mouseClick(launch_widget.launchTestnetLndNodeButton,
                         Qt.LeftButton)
        launch_widget.node_launcher.launchTestnetLndNode.assert_called_once()

    def test_launchMainnetLndNodeButton(self, qtbot, launch_widget):
        qtbot.mouseClick(launch_widget.launchMainnetLndNodeButton,
                         Qt.LeftButton)
        launch_widget.node_launcher.launchMainnetLndNode.assert_called_once()
