from unittest.mock import MagicMock, patch

import pytest
from PySide2.QtCore import Qt
from PySide2.QtGui import QClipboard
from PySide2.QtTest import QTest

from node_launcher.gui.network_buttons.joule_layout import JouleLayout


@pytest.fixture
def joule_layout() -> JouleLayout:
    node_set = MagicMock()
    node_set.lnd.rest_url = 'test rest'
    node_set.lnd.macaroon_path = 'test macaroon'
    joule_layout = JouleLayout(node_set)
    return joule_layout


class TestJouleLayout(object):
    def test_copy_rest(self, joule_layout: JouleLayout, qtbot: QTest):
        qtbot.mouseClick(joule_layout.copy_rest.button, Qt.LeftButton)
        assert QClipboard().text() == 'test rest'

    @patch('node_launcher.gui.network_buttons.joule_layout.reveal')
    def test_show_macaroons(self, reveal_patch: MagicMock,
                            joule_layout: JouleLayout, qtbot: QTest):
        qtbot.mouseClick(joule_layout.show_macaroons, Qt.LeftButton)
        reveal_patch.assert_called_with('test macaroon')
