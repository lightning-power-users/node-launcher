from node_launcher.gui.qt import Qt, QFont, QLabel


class PruneWarningLabel(QLabel):
    def __init__(self):
        super().__init__()
        new_font: QFont = self.font()
        new_font.setPointSize(8)
        self.setFont(new_font)
        self.setAlignment(Qt.AlignCenter | Qt.AlignCenter)

    def display_pruning_warning(self, prune: bool):
        text = ''
        if prune:
            text = 'Warning: pruning is on'
        self.setText(text)
        self.repaint()
