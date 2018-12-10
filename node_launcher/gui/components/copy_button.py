from PySide2.QtCore import QTimer
from PySide2.QtGui import QClipboard
from PySide2.QtWidgets import QVBoxLayout, QPushButton


class CopyButton(QVBoxLayout):
    def __init__(self, button_text: str, copy_text: str):
        super(CopyButton, self).__init__()
        self.copy_text = copy_text
        self.button_text = button_text
        self.button = QPushButton(button_text)
        # noinspection PyUnresolvedReferences
        self.button.clicked.connect(self.copy)
        self.addWidget(self.button)
        self.timer = QTimer(self.parentWidget())

    def copy(self):
        QClipboard().setText(self.copy_text)
        self.button.setText('Copied!')
        self.button.repaint()
        self.timer.singleShot(1000, self.remove_text)

    def remove_text(self):
        self.button.setText(self.button_text)
        self.button.repaint()
