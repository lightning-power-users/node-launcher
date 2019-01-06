from PySide2.QtWidgets import QWidget

from node_launcher.gui.advanced.versions_layout import VersionsLayout
from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.node_set import NodeSet


class AdvancedWidget(QWidget):
    def __init__(self, node_set: NodeSet):
        super().__init__()
        self.setWindowTitle('Advanced')
        self.node_set = node_set

        self.columns = 2

        self.layout = QGridLayout()

        self.versions_layout = VersionsLayout(node_set=node_set)
        self.layout.addLayout(self.versions_layout, column_span=self.columns)
        self.setLayout(self.layout)
