import pytest
from PySide2.QtCore import Qt
from PySide2.QtGui import QClipboard
from PySide2.QtTest import QTest

from node_launcher.gui.launch_widget import LaunchWidget


class TestGuiUnitTests(object):
    def test_testnet_bitcoin_qt_node_button(self, qtbot,
                                            launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.testnet_group_box.bitcoin_qt_button,
                         Qt.LeftButton)
        # noinspection PyUnresolvedReferences
        launch_widget.node_launcher.testnet_bitcoin_qt_node.assert_called_once()

    def test_mainnet_bitcoin_qt_node_button(self, qtbot,
                                            launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.mainnet_group_box.bitcoin_qt_button,
                         Qt.LeftButton)
        # noinspection PyUnresolvedReferences
        launch_widget.node_launcher.mainnet_bitcoin_qt_node.assert_called_once()

    def test_testnet_lnd_node_button(self, qtbot, launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.testnet_group_box.lnd_button,
                         Qt.LeftButton)
        # noinspection PyUnresolvedReferences
        launch_widget.node_launcher.testnet_lnd_node.assert_called_once()

    def test_mainnet_lnd_node_button(self, qtbot, launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.mainnet_group_box.lnd_button,
                         Qt.LeftButton)
        launch_widget.node_launcher.mainnet_lnd_node.assert_called_once()

    def test_testnet_lncli_copy_button(self, qtbot: QTest,
                                       launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.testnet_group_box.lncli_copy_button,
                         Qt.LeftButton)
        command = launch_widget.node_launcher.command_generator.testnet_lncli()
        assert QClipboard().text() == ' '.join(command)

    def test_mainnet_lncli_copy_button(self, qtbot: QTest,
                                       launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.mainnet_group_box.lncli_copy_button,
                         Qt.LeftButton)
        command = launch_widget.node_launcher.command_generator.mainnet_lncli()
        assert QClipboard().text() == ' '.join(command)

    def test_testnet_rest_url_copy_button(self, qtbot: QTest,
                                          launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.testnet_group_box.rest_url_copy_button,
                         Qt.LeftButton)
        rest_url = launch_widget.node_launcher.command_generator.testnet_rest_url()
        assert QClipboard().text() == rest_url

    def test_mainnet_rest_url_copy_button(self, qtbot: QTest,
                                          launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.mainnet_group_box.rest_url_copy_button,
                         Qt.LeftButton)
        rest_url = launch_widget.node_launcher.command_generator.mainnet_rest_url()
        assert QClipboard().text() == rest_url

    @pytest.mark.slow
    def test_reveal_macaroons(self, qtbot: QTest, launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.mainnet_group_box.show_macaroons_button,
                         Qt.LeftButton)
        qtbot.mouseClick(launch_widget.testnet_group_box.show_macaroons_button,
                         Qt.LeftButton)

    @pytest.mark.slow
    def test_reveal_datadir(self, qtbot: QTest, launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.data_directory_group_box.show_directory_button,
                         Qt.LeftButton)

    @pytest.mark.slow
    def test_select_datadir(self, qtbot: QTest, launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.data_directory_group_box.select_directory_button,
                         Qt.LeftButton)

    @pytest.mark.slow
    def test_unlock_wallet_button(self, qtbot: QTest, launch_widget: LaunchWidget):
        qtbot.mouseClick(launch_widget.mainnet_group_box.unlock_wallet_button,
                         Qt.LeftButton)
        assert launch_widget.mainnet_group_box.lnd_client.called_once()
