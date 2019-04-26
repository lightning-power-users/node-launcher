from PySide2.QtWidgets import QGridLayout, QTextEdit, QWidget, QTableView

from node_launcher.node_set import NodeSet


class ConfigurationWidget(QWidget):
    def __init__(self, node_set: NodeSet):
        super().__init__()
        self.node_set = node_set
        self.table = QTableView()
        self.table.setModel(self.node_set.bitcoind_node.configuration.model_repository)

        self.layout = QGridLayout()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
