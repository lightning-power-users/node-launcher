from unittest.mock import MagicMock

import pytest
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest

from node_launcher.gui.menu import TlsLayout


@pytest.fixture
def tls_layout():
    node_set = MagicMock()
    tls_layout = TlsLayout(node_set)
    return tls_layout


class TestTlsLayout(object):
    def test_reset_tls(self,
                       tls_layout: TlsLayout,
                       qtbot: QTest):
        qtbot.mouseClick(tls_layout.reset_tls, Qt.LeftButton)
        tls_layout.node_set.reset_tls.assert_called_once()
