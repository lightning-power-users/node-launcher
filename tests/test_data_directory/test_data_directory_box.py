from unittest.mock import patch, MagicMock

import pytest
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest

from node_launcher.gui.data_directory.data_directory_box import DataDirectoryBox


@pytest.fixture
def data_directory_box() -> DataDirectoryBox:
    data_directory_box = DataDirectoryBox()
    return data_directory_box


@patch('node_launcher.gui.data_directory.data_directory_box.QErrorMessage')
@patch('node_launcher.gui.data_directory.data_directory_box.QFileDialog')
@patch('node_launcher.gui.data_directory.data_directory_box.reveal')
class TestDataDirectoryBox(object):
    def test_show_directory_button(self,
                                   reveal_patch: MagicMock,
                                   qfiledialog_patch: MagicMock,
                                   qerrormessage_path: MagicMock,
                                   data_directory_box: DataDirectoryBox,
                                   qtbot: QTest
                                   ):
        qtbot.mouseClick(data_directory_box.show_directory_button, Qt.LeftButton)
        reveal_patch.assert_called_once()
