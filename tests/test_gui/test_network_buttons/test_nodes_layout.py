from unittest.mock import MagicMock

import pytest
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest

from node_launcher.constants import TESTNET
from node_launcher.gui.network_buttons.nodes_layout import NodesLayout


@pytest.fixture
def nodes_layout() -> NodesLayout:
    node_set = MagicMock()
    node_set.network = TESTNET
    nodes_layout = NodesLayout(node_set)
    return nodes_layout


class TestNodesLayout(object):
    def test_bitcoin_qt_button(self, nodes_layout: NodesLayout, qtbot: QTest):
        qtbot.mouseClick(nodes_layout.bitcoin_qt_button, Qt.LeftButton)
        nodes_layout.node_set.bitcoin.launch.assert_called_once()

    def test_lnd_button(self, nodes_layout: NodesLayout, qtbot: QTest):
        qtbot.mouseClick(nodes_layout.lnd_button, Qt.LeftButton)
        nodes_layout.node_set.lnd.launch.assert_called_once()
