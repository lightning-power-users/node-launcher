from PySide2.QtWidgets import QGridLayout, QWidget, QTableWidget, \
    QTableWidgetItem

from node_launcher.node_set import NodeSet


class ConfigurationWidget(QWidget):
    def __init__(self, node_set: NodeSet):
        super().__init__()
        self.node_set = node_set
        self.table = QTableWidget(0, 3)

        self.layout = QGridLayout()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        self.node_set.tor_node.configuration.line_change.connect(
            self.handle_line_change
        )
        self.node_set.bitcoind_node.configuration.line_change.connect(
            self.handle_line_change
        )
        self.node_set.lnd_node.configuration.line_change.connect(
            self.handle_line_change
        )
        self.rows = 0

    def refresh(self):
        self.table.resizeColumnsToContents()

    def handle_line_change(self, row_index: int, node_name: str, key: str, value: str):
        self.rows += 1
        row_number = self.table.rowCount()
        self.table.insertRow(row_number)
        for column_index, cell_text in enumerate([node_name, key, value]):
            item = QTableWidgetItem()
            item.setText(cell_text)
            self.table.setItem(row_number, column_index, item)
        self.refresh()
