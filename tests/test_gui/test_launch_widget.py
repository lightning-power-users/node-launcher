from unittest.mock import MagicMock

import pytest
from PySide2.QtCore import Qt
from PySide2.QtGui import QClipboard
from PySide2.QtTest import QTest

from node_launcher.command_generator import CommandGenerator
from node_launcher.configuration import Configuration
from node_launcher.configuration.bitcoin_configuration import BitcoinConfiguration
from node_launcher.gui.launch_widget import LaunchWidget
from node_launcher.node_launcher import NodeLauncher


@pytest.fixture
def mock_node_launcher():
    node_launcher = MagicMock()
    node_launcher.testnet_bitcoin_qt_node = MagicMock(return_value=None)
    node_launcher.mainnet_bitcoin_qt_node = MagicMock(return_value=None)
    node_launcher.testnet_lnd_node = MagicMock(return_value=None)
    node_launcher.mainnet_lnd_node = MagicMock(return_value=None)
    return node_launcher


@pytest.fixture
def integration_launch_widget():
    bitcoin_mainnet_conf = BitcoinConfiguration()
    bitcoin_testnet_conf = BitcoinConfiguration()
    command_generator = CommandGenerator(
        testnet_conf=Configuration('testnet', bitcoin_testnet_conf),
        mainnet_conf=Configuration('mainnet', bitcoin_mainnet_conf)
    )
    node_launcher = NodeLauncher(command_generator)
    launch_widget = LaunchWidget(node_launcher)
    return launch_widget


@pytest.fixture
def launch_widget(mock_node_launcher) -> LaunchWidget:
    launch_widget = LaunchWidget(mock_node_launcher)
    return launch_widget


class TestGuiUnitTests(object):
    def test_testnet_bitcoin_qt_node_button(self, qtbot, launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.testnet_group_box.bitcoin_qt_button,
                         Qt.LeftButton)
        launch_widget.node_launcher.testnet_bitcoin_qt_node.assert_called_once()

    def test_mainnet_bitcoin_qt_node_button(self, qtbot, launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.mainnet_group_box.bitcoin_qt_button,
                         Qt.LeftButton)
        launch_widget.node_launcher.mainnet_bitcoin_qt_node.assert_called_once()

    def test_testnet_lnd_node_button(self, qtbot, launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.testnet_group_box.lnd_button,
                         Qt.LeftButton)
        launch_widget.node_launcher.testnet_lnd_node.assert_called_once()

    def test_mainnet_lnd_node_button(self, qtbot, launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.mainnet_group_box.lnd_button,
                         Qt.LeftButton)
        launch_widget.node_launcher.mainnet_lnd_node.assert_called_once()

    def test_testnet_lncli_copy_button(self, qtbot: QTest, integration_launch_widget: LaunchWidget):
        qtbot.mouseClick(integration_launch_widget.testnet_group_box.lncli_copy_button,
                         Qt.LeftButton)
        command = integration_launch_widget.node_launcher.command_generator.testnet_lncli()
        assert QClipboard().text() == ' '.join(command)

    def test_mainnet_lncli_copy_button(self, qtbot: QTest, integration_launch_widget: LaunchWidget):
        qtbot.mouseClick(integration_launch_widget.mainnet_group_box.lncli_copy_button,
                         Qt.LeftButton)
        command = integration_launch_widget.node_launcher.command_generator.mainnet_lncli()
        assert QClipboard().text() == ' '.join(command)

    def test_testnet_rest_url_copy_button(self, qtbot: QTest, integration_launch_widget: LaunchWidget):
        qtbot.mouseClick(integration_launch_widget.testnet_group_box.rest_url_copy_button,
                         Qt.LeftButton)
        rest_url = integration_launch_widget.node_launcher.command_generator.testnet_rest_url()
        assert QClipboard().text() == rest_url

    def test_mainnet_rest_url_copy_button(self, qtbot: QTest, integration_launch_widget: LaunchWidget):
        qtbot.mouseClick(integration_launch_widget.mainnet_group_box.rest_url_copy_button,
                         Qt.LeftButton)
        rest_url = integration_launch_widget.node_launcher.command_generator.mainnet_rest_url()
        assert QClipboard().text() == rest_url

    @pytest.mark.slow
    def test_reveal(self, qtbot: QTest, integration_launch_widget: LaunchWidget):
        qtbot.mouseClick(integration_launch_widget.mainnet_group_box.show_macaroons_button,
                         Qt.LeftButton)
        qtbot.mouseClick(integration_launch_widget.testnet_group_box.show_macaroons_button,
                         Qt.LeftButton)
