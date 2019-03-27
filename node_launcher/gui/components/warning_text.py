from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel


class WarningText(QLabel):
    def __init__(self, text: str):
        super().__init__()
        self.setStyleSheet("QLabel {color: red}")
        self.setText(text)