from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel


class DatadirLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.datadir = None
        self.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.setFixedHeight(50)

    def set_datadir(self, datadir: str):
        self.datadir = datadir
        self.setText(self.datadir)
