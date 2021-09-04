from node_launcher.gui.qt import QLabel


class WarningText(QLabel):
    def __init__(self, text: str):
        super().__init__()
        self.setStyleSheet("QLabel {color: red}")
        self.setText(text)