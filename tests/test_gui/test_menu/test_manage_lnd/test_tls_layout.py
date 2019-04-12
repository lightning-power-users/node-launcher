from unittest.mock import MagicMock

import pytest
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest

from node_launcher.gui.menu.manage_lnd import TlsLayout


@pytest.fixture
def tls_layout():
    lnd = MagicMock()
    tls_layout = TlsLayout(lnd)
    return tls_layout


class TestTlsLayout(object):
    def test_reset_tls(self,
                       tls_layout: TlsLayout,
                       qtbot: QTest):
        qtbot.mouseClick(tls_layout.reset_tls, Qt.LeftButton)
        tls_layout.lnd.reset_tls.assert_called_once()
