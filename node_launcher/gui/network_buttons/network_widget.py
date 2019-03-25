from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QWidget

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.network_buttons.advanced import CliLayout
from node_launcher.node_set import NodeSet
from . import JouleLayout, NodesLayout, RestartLayout


class NetworkWidget(QWidget):
    node_set: NodeSet
    timer = QTimer

    def __init__(self):
        super().__init__()

        self.timer = QTimer(self.parentWidget())

        self.node_set = NodeSet()

        columns = 2

        layout = QGridLayout()

        self.nodes_layout = NodesLayout(node_set=self.node_set)
        layout.addLayout(self.nodes_layout, column_span=columns)
        self.joule_layout = JouleLayout(node_set=self.node_set)
        layout.addLayout(self.joule_layout, column_span=columns)

        self.cli_layout = CliLayout(node_set=self.node_set)
        layout.addLayout(self.cli_layout, column_span=columns)

        self.restart_layout = RestartLayout(node_set=self.node_set)
        layout.addLayout(self.restart_layout)

        self.setLayout(layout)
