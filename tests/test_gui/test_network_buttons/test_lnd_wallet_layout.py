from unittest.mock import MagicMock, patch

import pytest
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QWidget

from node_launcher.gui.network_buttons.lnd_wallet_layout import LndWalletLayout


@pytest.fixture
def lnd_wallet_layout() -> LndWalletLayout:
    node_set = MagicMock()
    node_set.network = 'mainnet'
    lnd_wallet_layout = LndWalletLayout(QWidget(), node_set)
    return lnd_wallet_layout


class TestLndWalletLayout(object):
    @patch('node_launcher.gui.network_buttons.lnd_wallet_layout.keyring')
    @patch('node_launcher.gui.network_buttons.lnd_wallet_layout.QInputDialog')
    def test_unlock_wallet(self,
                           input_dialog_patch: MagicMock,
                           keyring_patch: MagicMock,
                           lnd_wallet_layout: LndWalletLayout, qtbot: QTest):
        input_dialog_patch.getText = MagicMock(return_value=('password', True))
        qtbot.mouseClick(lnd_wallet_layout.unlock_wallet_button, Qt.LeftButton)
        input_dialog_patch.getText.assert_called()
        lnd_wallet_layout.node_set.lnd_client.unlock.assert_called()
        keyring_patch.set_password.assert_called()

    @patch('node_launcher.gui.network_buttons.lnd_wallet_layout.keyring')
    @patch('node_launcher.gui.network_buttons.lnd_wallet_layout.QInputDialog')
    @patch('node_launcher.gui.network_buttons.lnd_wallet_layout.SeedDialog')
    def test_create_wallet(self,
                           seed_dialog_patch: MagicMock,
                           input_dialog_patch: MagicMock,
                           keyring_patch: MagicMock,
                           lnd_wallet_layout: LndWalletLayout,
                           qtbot: QTest):
        input_dialog_patch.getText = MagicMock(return_value=('password', True))
        qtbot.mouseClick(lnd_wallet_layout.create_wallet_button, Qt.LeftButton)
        input_dialog_patch.getText.assert_called()
        lnd_wallet_layout.node_set.lnd_client.generate_seed.assert_called()
        seed_dialog_patch.assert_called()
        keyring_patch.set_password.assert_called()

    @patch('node_launcher.gui.network_buttons.lnd_wallet_layout.keyring')
    @patch('node_launcher.gui.network_buttons.lnd_wallet_layout.QInputDialog')
    def test_recover_wallet(self,
                            input_dialog_patch: MagicMock,
                            keyring_patch: MagicMock,
                            lnd_wallet_layout: LndWalletLayout,
                            qtbot: QTest):
        input_dialog_patch.getText = MagicMock(return_value=('password', True))
        qtbot.mouseClick(lnd_wallet_layout.recover_wallet_button, Qt.LeftButton)
        input_dialog_patch.getText.assert_called()
        lnd_wallet_layout.node_set.lnd_client.initialize_wallet.assert_called()
        keyring_patch.set_password.assert_called()
