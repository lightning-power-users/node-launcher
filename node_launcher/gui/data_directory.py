import os

from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QLabel, QFileDialog, QErrorMessage

from node_launcher.gui.utilities import reveal
from node_launcher.node_set.node_set import NodeSet


class DataDirectoryBox(QtWidgets.QGroupBox):
    node_set: NodeSet

    def __init__(self, node_set: NodeSet):
        super().__init__('Bitcoin Data Directory')
        self.error_message = QErrorMessage(self)

        self.node_set = node_set
        self.datadir = self.node_set.bitcoin.file['datadir']
        self.datadir_label = QLabel()
        self.datadir_label.setText(self.datadir)
        self.datadir_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.datadir_label.setFixedHeight(50)

        self.prune_warning_label = QLabel()
        new_font: QFont = self.prune_warning_label.font()
        new_font.setPointSize(8)
        self.prune_warning_label.setFont(new_font)
        self.prune_warning_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.display_pruning_warning()

        self.show_directory_button = QtWidgets.QPushButton('Show Directory')
        # noinspection PyUnresolvedReferences
        self.show_directory_button.clicked.connect(
            lambda: reveal(self.datadir)
        )

        self.select_directory_button = QtWidgets.QPushButton('Select Directory')
        # noinspection PyUnresolvedReferences
        self.select_directory_button.clicked.connect(self.file_dialog)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.datadir_label, 1, 1, 1, 2)
        layout.addWidget(self.prune_warning_label, 2, 1, 1, 2)
        layout.addWidget(self.show_directory_button, 3, 1)
        layout.addWidget(self.select_directory_button, 3, 2)
        self.setLayout(layout)
        self.setFixedWidth(self.minimumSizeHint().width())

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
        self.node_set.bitcoin.file['datadir'] = data_directory
        self.node_set.bitcoin.set_prune()
        self.datadir = data_directory
        self.datadir_label.setText(data_directory)
        self.display_pruning_warning()

    def display_pruning_warning(self):
        if self.node_set.bitcoin.file['prune']:
            self.prune_warning_label.setText('Warning: pruning is on')
            self.prune_warning_label.repaint()
        else:
            self.prune_warning_label.setText('')
            self.prune_warning_label.repaint()
