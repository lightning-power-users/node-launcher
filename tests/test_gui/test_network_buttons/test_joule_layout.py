from unittest.mock import MagicMock, patch

import pytest
from PySide2.QtCore import Qt
from PySide2.QtGui import QClipboard
from PySide2.QtTest import QTest
from PySide2.QtWidgets import QWidget

from node_launcher.gui.system_tray import SystemTray


@pytest.fixture
def system_tray() -> SystemTray:
    node_set = MagicMock()
    node_set.lnd.rest_url = 'test rest'
    node_set.lnd.macaroon_path = 'test macaroon'
    system_tray = SystemTray(parent=QWidget(), node_set=node_set)
    return system_tray


class TestJouleLayout(object):
    def test_copy_rest(self, system_tray: SystemTray, qtbot: QTest):
        system_tray.menu.joule_url_action.trigger()
        assert QClipboard().text() == 'test rest'

    @patch('node_launcher.gui.system_tray.reveal')
    def test_show_macaroons(self, reveal_patch: MagicMock,
                            system_tray: SystemTray, qtbot: QTest):
        system_tray.menu.joule_macaroons_action.trigger()
        reveal_patch.assert_called_with('test macaroon')
