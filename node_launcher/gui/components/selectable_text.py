from node_launcher.gui.qt import Qt, QLabel


class SelectableText(QLabel):
    def __init__(self, text: str):
        super().__init__()
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setText(text)
