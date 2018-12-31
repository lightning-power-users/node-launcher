import pytest
from PySide2.QtCore import Qt
from PySide2.QtGui import QClipboard
from PySide2.QtTest import QTest

from node_launcher.gui.components.copy_button import CopyButton


@pytest.fixture
def copy_button() -> CopyButton:
    copy_button = CopyButton(button_text='Test Me', copy_text='copy_this')
    return copy_button


class TestCopyButton(object):
    def test_copy_button(self, copy_button: CopyButton, qtbot: QTest):
        qtbot.mouseClick(copy_button.button, Qt.LeftButton)
        assert QClipboard().text() == 'copy_this'
