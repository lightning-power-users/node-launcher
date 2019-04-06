from unittest.mock import patch, MagicMock

import pytest
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest

from node_launcher.gui.menu import DataDirectoryBox
from node_launcher.node_set import NodeSet


@pytest.fixture
def data_directory_box() -> DataDirectoryBox:
    data_directory_box = DataDirectoryBox(bitcoin=NodeSet().bitcoin)
    data_directory_box.file_dialog = MagicMock()
    return data_directory_box


@patch('node_launcher.gui.menu.settings.data_directories.data_directory_box.SelectDirectoryDialog')
@patch('node_launcher.gui.menu.settings.data_directories.data_directory_box.reveal')
class TestDataDirectoryBox(object):
    def test_show_directory_button(self,
                                   reveal_patch: MagicMock,
                                   select_directory_dialog_patch: MagicMock,
                                   data_directory_box: DataDirectoryBox,
                                   qtbot: QTest
                                   ):
        qtbot.mouseClick(data_directory_box.show_directory_button,
                         Qt.LeftButton)
        reveal_patch.assert_called_once()

    def test_select_directory_button(self,
                                     reveal_patch: MagicMock,
                                     select_directory_dialog_patch: MagicMock,
                                     data_directory_box: DataDirectoryBox,
                                     qtbot: QTest
                                     ):
        qtbot.mouseClick(data_directory_box.select_directory_button,
                         Qt.LeftButton)
        data_directory_box.file_dialog.select_new.assert_called_once()
