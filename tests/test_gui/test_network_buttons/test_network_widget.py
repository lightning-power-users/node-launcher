from unittest.mock import MagicMock, patch

import pytest
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QWidget

from node_launcher.gui.network_buttons.network_widget import NetworkWidget


@pytest.fixture
def network_widget() -> NetworkWidget:
    node_set = MagicMock()
    node_set.network = 'mainnet'
    network_widget = NetworkWidget(QWidget(), node_set)
    return network_widget


class TestNetworkWidget(object):
    @patch('node_launcher.gui.network_buttons.network_widget.keyring')
    @patch('node_launcher.gui.network_buttons.network_widget.QInputDialog')
    def test_unlock_wallet(self,
                           input_dialog_patch: MagicMock,
                           keyring_patch: MagicMock,
                           network_widget: NetworkWidget, qtbot: QTest):
        input_dialog_patch.getText = MagicMock(return_value=('password', True))
        qtbot.mouseClick(network_widget.unlock_wallet_button, Qt.LeftButton)
        input_dialog_patch.getText.assert_called()
        network_widget.node_set.lnd_client.unlock.assert_called()
        keyring_patch.set_password.assert_called()

    @patch('node_launcher.gui.network_buttons.network_widget.keyring')
    @patch('node_launcher.gui.network_buttons.network_widget.QInputDialog')
    @patch('node_launcher.gui.network_buttons.network_widget.SeedDialog')
    def test_create_wallet(self,
                           seed_dialog_patch: MagicMock,
                           input_dialog_patch: MagicMock,
                           keyring_patch: MagicMock,
                           network_widget: NetworkWidget,
                           qtbot: QTest):
        input_dialog_patch.getText = MagicMock(return_value=('password', True))
        qtbot.mouseClick(network_widget.create_wallet_button, Qt.LeftButton)
        input_dialog_patch.getText.assert_called()
        network_widget.node_set.lnd_client.generate_seed.assert_called()
        seed_dialog_patch.assert_called()
        keyring_patch.set_password.assert_called()

    @patch('node_launcher.gui.network_buttons.network_widget.keyring')
    @patch('node_launcher.gui.network_buttons.network_widget.QInputDialog')
    def test_recover_wallet(self,
                            input_dialog_patch: MagicMock,
                            keyring_patch: MagicMock,
                            network_widget: NetworkWidget,
                            qtbot: QTest):
        input_dialog_patch.getText = MagicMock(return_value=('password', True))
        qtbot.mouseClick(network_widget.recover_wallet_button, Qt.LeftButton)
        input_dialog_patch.getText.assert_called()
        network_widget.node_set.lnd_client.initialize_wallet.assert_called()
        keyring_patch.set_password.assert_called()
