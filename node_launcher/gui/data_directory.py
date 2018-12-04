import os

from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel, QFileDialog, QErrorMessage

from node_launcher.command_generator import CommandGenerator
from node_launcher.utilities import reveal


class DataDirectoryBox(QtWidgets.QGroupBox):
    def __init__(self, command_generator: CommandGenerator):
        super().__init__('Bitcoin Data Directory')
        self.error_message = QErrorMessage(self)

        self.command_generator = command_generator
        self.datadir = self.command_generator.testnet.bitcoin.file.datadir
        self.datadir_label = QLabel()
        self.datadir_label.setText(self.datadir)
        self.datadir_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.datadir_label.setFixedHeight(50)

        self.show_directory_button = QtWidgets.QPushButton('Show Directory')
        # noinspection PyUnresolvedReferences
        self.show_directory_button.clicked.connect(self.reveal_datadir)

        self.select_directory_button = QtWidgets.QPushButton('Select Directory')
        # noinspection PyUnresolvedReferences
        self.select_directory_button.clicked.connect(self.file_dialog)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.datadir_label, 1, 1, 1, 2)
        layout.addWidget(self.show_directory_button, 2, 1)
        layout.addWidget(self.select_directory_button, 2, 2)

        self.setLayout(layout)

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
        self.command_generator.testnet.bitcoin.file.datadir = data_directory
        self.command_generator.mainnet.bitcoin.set_prune()
        self.datadir = data_directory
        self.datadir_label.setText(data_directory)

    def reveal_datadir(self):
        try:
            reveal(self.datadir)
        except (NotADirectoryError, FileNotFoundError):
            self.error_message.showMessage(f'{self.datadir} not found')
            return
