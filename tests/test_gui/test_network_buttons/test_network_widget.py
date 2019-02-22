from unittest.mock import MagicMock, patch

import pytest
from PySide2.QtTest import QTest

from node_launcher.gui.network_buttons.network_widget import NetworkWidget


@pytest.fixture
def network_widget() -> NetworkWidget:
    network_widget = NetworkWidget()
    network_widget.timer = MagicMock()
    network_widget.node_set = MagicMock()
    return network_widget


@patch('node_launcher.gui.network_buttons.network_widget.QTimer')
@patch('node_launcher.gui.network_buttons.network_widget.NodeSet')
class TestNetworkWidget(object):
    def test_refresh(self,
                     node_set_patch: MagicMock,
                     timer_patch: MagicMock,
                     network_widget: NetworkWidget,
                     qtbot: QTest):
        network_widget.refresh()
        network_widget.node_set.bitcoin.check_process.assert_called()
        network_widget.node_set.lnd.check_process.assert_called()
