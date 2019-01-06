from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel


class SelectableText(QLabel):
    def __init__(self, text: str):
        super().__init__()
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setText(text)
