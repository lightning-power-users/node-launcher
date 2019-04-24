from unittest.mock import MagicMock, patch

import pytest
from PySide2.QtGui import QClipboard
from PySide2.QtTest import QTest

from node_launcher.gui.menu.menu import Menu


@pytest.fixture
def menu() -> Menu:
    system_tray = MagicMock()
    node_set = MagicMock()
    node_set.lnd_node.configuration.rest_url = 'test rest'
    node_set.lnd_node.configuration.macaroon_path = 'test macaroon'
    menu = Menu(node_set=node_set, system_tray=system_tray)
    return menu


@patch('node_launcher.gui.menu.menu.webbrowser')
@patch('node_launcher.gui.menu.menu.reveal')
class TestMenu(object):
    def test_joule_url_action(self,
                              reveal_patch: MagicMock,
                              webbrowser_patch: MagicMock,
                              menu: Menu,
                              qtbot: QTest):
        menu.joule_url_action.trigger()
        assert QClipboard().text() == 'test rest'

    def test_joule_macaroons_action(self,
                                    reveal_patch: MagicMock,
                                    webbrowser_patch: MagicMock,
                                    menu: Menu,
                                    qtbot: QTest):
        menu.joule_macaroons_action.trigger()
        reveal_patch.assert_called_with('test macaroon')

    def test_zap_open_action(self,
                             reveal_patch: MagicMock,
                             webbrowser_patch: MagicMock,
                             menu: Menu,
                             qtbot: QTest):
        menu.zap_open_action.trigger()
        webbrowser_patch.open.assert_called_once()
