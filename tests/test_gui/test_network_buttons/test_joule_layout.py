from unittest.mock import MagicMock, patch

import pytest
from PySide2.QtGui import QClipboard
from PySide2.QtTest import QTest

from node_launcher.gui.menu import Menu


@pytest.fixture
def menu() -> Menu:
    system_tray = MagicMock()
    node_set = MagicMock()
    node_set.lnd.rest_url = 'test rest'
    node_set.lnd.macaroon_path = 'test macaroon'
    menu = Menu(node_set=node_set, system_tray=system_tray)
    return menu


class TestJouleLayout(object):
    def test_copy_rest(self, menu: Menu, qtbot: QTest):
        menu.joule_url_action.trigger()
        assert QClipboard().text() == 'test rest'

    @patch('node_launcher.gui.menu.reveal')
    def test_show_macaroons(self, reveal_patch: MagicMock,
                            menu: Menu, qtbot: QTest):
        menu.joule_macaroons_action.trigger()
        reveal_patch.assert_called_with('test macaroon')
