from unittest.mock import MagicMock, patch

import pytest
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QWidget

from node_launcher.constants import MAINNET
from node_launcher.gui.network_buttons.network_widget import NetworkWidget


@pytest.fixture
def network_widget() -> NetworkWidget:
    network_widget = NetworkWidget(
        parent=QWidget(),
        network=MAINNET
    )
    network_widget.threadpool = MagicMock()
    network_widget.timer = MagicMock()
    return network_widget


@patch('node_launcher.gui.network_buttons.network_widget.QTimer')
@patch('node_launcher.gui.network_buttons.network_widget.Worker')
@patch('node_launcher.gui.network_buttons.network_widget.QThreadPool')
@patch('node_launcher.gui.network_buttons.network_widget.QErrorMessage')
@patch('node_launcher.gui.network_buttons.network_widget.keyring')
@patch('node_launcher.gui.network_buttons.network_widget.NodeSet')
class TestNetworkWidget(object):
    def test_auto_unlock_wallet(self,
                                node_set_patch: MagicMock,
                                keyring_patch: MagicMock,
                                error_message_patch: MagicMock,
                                thread_pool_patch: MagicMock,
                                worker_patch: MagicMock,
                                timer_patch: MagicMock,
                                network_widget: NetworkWidget,
                                qtbot: QTest):
        network_widget.auto_unlock_wallet()
        keyring_patch.get_password.assert_called()
        worker_patch.assert_called()
        network_widget.threadpool.start.assert_called()
