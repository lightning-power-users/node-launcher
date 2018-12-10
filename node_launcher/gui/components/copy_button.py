from PySide2.QtGui import QClipboard
from PySide2.QtWidgets import QVBoxLayout, QPushButton


class CopyButton(QVBoxLayout):
    def __init__(self, button_text: str, copy_text: str):
        super(CopyButton, self).__init__()
        self.button = QPushButton(button_text)
        # noinspection PyUnresolvedReferences
        self.button.clicked.connect(lambda: QClipboard().setText(copy_text))
        self.addWidget(self.button)
