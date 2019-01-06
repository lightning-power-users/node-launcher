from PySide2.QtWidgets import QWidget, QVBoxLayout

from node_launcher.node_set import NodeSet


class AdvancedWidget(QWidget):
    def __init__(self, node_set: NodeSet):
        super().__init__()
        self.setWindowTitle('Advanced')
        self.node_set = node_set

        self.grid = QVBoxLayout()
        self.grid.addStretch()
        self.setLayout(self.grid)
