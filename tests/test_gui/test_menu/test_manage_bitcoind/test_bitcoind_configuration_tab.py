from unittest.mock import MagicMock, patch

import pytest
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest

from node_launcher.constants import (
    BITCOIN_MAINNET_PEER_PORT,
    BITCOIN_MAINNET_RPC_PORT,
    TARGET_BITCOIN_RELEASE
)
from node_launcher.gui.menu.manage_bitcoind import BitcoindConfigurationTab


@pytest.fixture
def bitcoind_configuration_tab() -> BitcoindConfigurationTab:
    bitcoin = MagicMock()
    bitcoin.file.directory = '/test/bitcoin'
    bitcoin.software.release_version = TARGET_BITCOIN_RELEASE
    tab = BitcoindConfigurationTab(bitcoin)
    return tab


class TestBitcoindConfigurationTab(object):
    @patch(
        'node_launcher.gui.menu.manage_bitcoind.bitcoind_configuration_tab.reveal')
    def test_show_bitcoin_conf(self,
                               reveal_patch: MagicMock,
                               bitcoind_configuration_tab,
                               qtbot: QTest):

        qtbot.mouseClick(bitcoind_configuration_tab.show_bitcoin_conf,
                         Qt.LeftButton)
        reveal_patch.assert_called_with('/test/bitcoin')

    def test_bitcoin_version(self,
                             bitcoind_configuration_tab,
                             qtbot: QTest):
        assert bitcoind_configuration_tab.bitcoin_version.text().endswith(
            TARGET_BITCOIN_RELEASE
        )
