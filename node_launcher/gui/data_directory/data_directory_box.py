import os

from PySide2.QtCore import Signal
from PySide2.QtWidgets import (
    QErrorMessage,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QPushButton
)

from node_launcher.gui.data_directory import DatadirLabel, PruneWarningLabel
from node_launcher.gui.utilities import reveal


class DataDirectoryBox(QGroupBox):
    new_data_directory = Signal(str)

    def __init__(self):
        super().__init__('Bitcoin Data Directory')
        self.error_message = QErrorMessage(self)

        self.datadir = None

        self.datadir_label = DatadirLabel()
        self.prune_warning_label = PruneWarningLabel()

        self.show_directory_button = QPushButton('Show Directory')
        # noinspection PyUnresolvedReferences
        self.show_directory_button.clicked.connect(
            lambda: reveal(self.datadir)
        )

        self.select_directory_button = QPushButton('Select Directory')
        # noinspection PyUnresolvedReferences
        self.select_directory_button.clicked.connect(self.file_dialog)

        layout = QGridLayout()
        layout.addWidget(self.datadir_label, 1, 1, 1, 2)
        layout.addWidget(self.prune_warning_label, 2, 1, 1, 2)
        layout.addWidget(self.show_directory_button, 3, 1)
        layout.addWidget(self.select_directory_button, 3, 2)
        self.setLayout(layout)
        self.setFixedWidth(self.minimumSizeHint().width())

    def set_datadir(self, datadir: str, prune: bool):
        self.datadir = datadir
        self.datadir_label.set_datadir(self.datadir)
        self.prune_warning_label.display_pruning_warning(prune)

    def file_dialog(self):
        # noinspection PyCallByClass
        data_directory = QFileDialog.getExistingDirectory(self,
                                                          'Select Data Directory',
                                                          self.datadir,
                                                          QFileDialog.ShowDirsOnly
                                                          | QFileDialog.DontResolveSymlinks)
        if not data_directory:
            return
        if not os.path.isdir(data_directory):
            self.error_message.showMessage('Directory does not exist, please try again!')

        # noinspection PyUnresolvedReferences
        self.new_data_directory.emit(data_directory)
