from PySide2 import QtWidgets
from PySide2.QtWidgets import QLineEdit

from node_launcher.command_generator import CommandGenerator


class DataDirectoryBox(QtWidgets.QGroupBox):
    def __init__(self, command_generator: CommandGenerator):
        super().__init__('Data Directory')

        datadir = QLineEdit()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(datadir)
        self.setLayout(layout)
