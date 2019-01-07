from PySide2.QtWidgets import QWidget

from node_launcher.gui.advanced.actions_layout import ActionsLayout
from node_launcher.gui.advanced.ports_layout import PortsLayout
from node_launcher.gui.advanced.versions_layout import VersionsLayout
from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.horizontal_line import HorizontalLine
from node_launcher.node_set import NodeSet


class AdvancedWidget(QWidget):
    def __init__(self, node_set: NodeSet):
        super().__init__()
        self.setWindowTitle('Advanced')
        self.node_set = node_set

        self.columns = 2

        self.layout = QGridLayout()

        self.versions_layout = VersionsLayout(node_set=node_set)
        self.ports_layout = PortsLayout(node_set=node_set)
        self.actions_layout = ActionsLayout(node_set=node_set)

        self.layout.addLayout(self.versions_layout, column_span=self.columns)
        self.layout.addWidget(HorizontalLine(), column_span=self.columns)
        self.layout.addLayout(self.ports_layout, column_span=self.columns)
        self.layout.addWidget(HorizontalLine(), column_span=self.columns)
        self.layout.addLayout(self.actions_layout, column_span=self.columns)
        self.setLayout(self.layout)
