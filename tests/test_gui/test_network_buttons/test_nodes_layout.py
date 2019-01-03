from unittest.mock import MagicMock

import pytest
from PySide2.QtCore import Qt
from PySide2.QtGui import QClipboard
from PySide2.QtTest import QTest

from node_launcher.gui.network_buttons.cli_layout import CliLayout


@pytest.fixture
def cli_layout() -> CliLayout:
    node_set = MagicMock()
    node_set.bitcoin.bitcoin_cli = 'test bitcoin-cli'
    node_set.lnd.lncli = 'test lncli'
    cli_layout = CliLayout(node_set)
    return cli_layout


class TestCliLayout(object):
    def test_copy_bitcoin_cli(self, cli_layout: CliLayout, qtbot: QTest):
        qtbot.mouseClick(cli_layout.copy_bitcoin_cli.button, Qt.LeftButton)
        assert QClipboard().text() == 'test bitcoin-cli'

    def test_copy_lncli(self, cli_layout: CliLayout, qtbot: QTest):
        qtbot.mouseClick(cli_layout.copy_lncli.button, Qt.LeftButton)
        assert QClipboard().text() == 'test lncli'
