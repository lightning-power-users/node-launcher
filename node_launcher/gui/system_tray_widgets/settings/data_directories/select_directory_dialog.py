import os

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QFileDialog, QWidget, QErrorMessage


class SelectDirectoryDialog(QFileDialog):
    new_data_directory = Signal(str)

    def __init__(self, parent: QWidget):
        super().__init__(parent, 'Select Data Directory')
        self.setFileMode(QFileDialog.DirectoryOnly)
        options = QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        self.setOptions(options)
        self.setViewMode(QFileDialog.Detail)
        self.error_message = QErrorMessage(self)

    def select_new(self, current_datadir: str):
        self.setDirectory(current_datadir)
        if self.exec_():
            new_datadir = self.selectedFiles()[0]
            if not new_datadir:
                return
            if not os.path.isdir(new_datadir):
                self.error_message.showMessage(
                    'Directory does not exist, please try again!'
                )
                self.select_new(current_datadir)
            # noinspection PyUnresolvedReferences
            self.new_data_directory.emit(new_datadir)
