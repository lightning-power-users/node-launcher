from unittest.mock import patch, MagicMock

import pytest
from PySide2.QtCore import Qt
from PySide2.QtGui import QClipboard
from PySide2.QtTest import QTest

from node_launcher.gui.launch_widget import LaunchWidget
from node_launcher.node_set.bitcoin import Bitcoin
from node_launcher.node_set.lnd import Lnd
from node_launcher.node_set.lnd_client import LndClient


class TestGuiUnitTests(object):

    @patch.object(Bitcoin, 'launch')
    def test_bitcoin_qt_node_button(self, mock_bitcoin_launch: MagicMock, qtbot: QTest):
        launch_widget = LaunchWidget()
        qtbot.mouseClick(launch_widget.testnet_group_box.nodes_layout.bitcoin_qt_button,
                         Qt.LeftButton)
        mock_bitcoin_launch.assert_called_once()

    @patch.object(Lnd, 'launch')
    def test_lnd_node_button(self, mock_lnd_launch: MagicMock, qtbot: QTest):
        launch_widget = LaunchWidget()
        launch_widget.testnet_group_box.nodes_layout.lnd_button.setEnabled(True)
        qtbot.mouseClick(launch_widget.testnet_group_box.nodes_layout.lnd_button,
                         Qt.LeftButton)
        mock_lnd_launch.assert_called_once()

    def test_lncli_copy_button(self, qtbot: QTest,
                               launch_widget: LaunchWidget):
        launch_widget.testnet_group_box.cli_layout.copy_lncli.button.setEnabled(True)
        qtbot.mouseClick(launch_widget.testnet_group_box.cli_layout.copy_lncli.button,
                         Qt.LeftButton)
        command = launch_widget.testnet_group_box.node_set.lnd.lncli
        assert QClipboard().text() == ' '.join(command)

    def test_rest_url_copy_button(self, qtbot: QTest,
                                  launch_widget: LaunchWidget):
        launch_widget.testnet_group_box.joule_layout.copy_rest.button.setEnabled(True)
        qtbot.mouseClick(launch_widget.testnet_group_box.joule_layout.copy_rest.button,
                         Qt.LeftButton)
        rest_url = launch_widget.testnet_group_box.node_set.lnd.rest_url
        assert QClipboard().text() == rest_url

    @pytest.mark.slow
    def test_reveal_macaroons(self, qtbot: QTest, launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.testnet_group_box.joule_layout.show_macaroons_button,
                         Qt.LeftButton)

    @pytest.mark.slow
    def test_reveal_datadir(self, qtbot: QTest, launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.data_directory_group_box.show_directory_button,
                         Qt.LeftButton)

    @pytest.mark.slow
    def test_select_datadir(self, qtbot: QTest, launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.data_directory_group_box.select_directory_button,
                         Qt.LeftButton)

    @patch.object(LndClient, 'unlock')
    def test_unlock_wallet_button(self, mock_unlock: MagicMock, qtbot: QTest, launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.testnet_group_box.lnd_wallet_layout.unlock_wallet_button,
                         Qt.LeftButton)
        assert mock_unlock.called_once()
