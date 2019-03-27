from PySide2.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QPushButton
)

from .data_directories import DatadirLabel, PruneWarningLabel
from .data_directories import SelectDirectoryDialog
from node_launcher.gui.utilities import reveal


class DataDirectoryBox(QGroupBox):

    def __init__(self):
        super().__init__('Bitcoin Data Directory')
        self.file_dialog = SelectDirectoryDialog(self)

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
        self.select_directory_button.clicked.connect(
            lambda: self.file_dialog.select_new(current_datadir=self.datadir)
        )

        layout = QGridLayout(self)
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
