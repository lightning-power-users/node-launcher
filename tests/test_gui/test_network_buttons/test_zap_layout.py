from unittest.mock import MagicMock, patch

import pytest
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest

from node_launcher.constants import TESTNET
from node_launcher.gui.menu import ZapLayout


@pytest.fixture
def zap_layout() -> ZapLayout:
    node_set = MagicMock()
    node_set.network = TESTNET
    zap_layout = ZapLayout(node_set)
    return zap_layout


@patch(
    'node_launcher.gui.menu.advanced.zap_layout.get_deprecated_lndconnect_url')
@patch('node_launcher.gui.menu.advanced.zap_layout.get_qrcode_img')
@patch('node_launcher.gui.menu.advanced.zap_layout.webbrowser')
@patch('node_launcher.gui.menu.advanced.zap_layout.QPixmap')
@patch('node_launcher.gui.menu.advanced.zap_layout.QLabel')
class TestZapLayout(object):
    def test_open_zap_desktop_button(self,
                                     qlabel_patch: MagicMock,
                                     qpixmap_patch: MagicMock,
                                     webbrowser_patch: MagicMock,
                                     get_qrcode_img_patch: MagicMock,
                                     get_deprecated_lndconnect_url_patch: MagicMock,
                                     zap_layout: ZapLayout,
                                     qtbot: QTest):
        qtbot.mouseClick(zap_layout.open_zap_desktop_button, Qt.LeftButton)
        get_deprecated_lndconnect_url_patch.assert_called_once()
        webbrowser_patch.open.assert_called_once()
'''
    def test_show_zap_qrcode(self,
                             qlabel_patch: MagicMock,
                             qpixmap_patch: MagicMock,
                             webbrowser_patch: MagicMock,
                             get_qrcode_img_patch: MagicMock,
                             get_deprecated_lndconnect_url_patch: MagicMock,
                             zap_layout: ZapLayout,
                             qtbot: QTest):
        qtbot.mouseClick(zap_layout.show_zap_qrcode_button, Qt.LeftButton)
        get_qrcode_img_patch.assert_called_once()
        qpixmap_patch.assert_called_once()
'''
