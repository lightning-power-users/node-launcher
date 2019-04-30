from PySide2.QtCore import Qt
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
            self.handle_configuration_file_line_change
        )
        self.node_set.bitcoind_node.configuration.line_change.connect(
            self.handle_configuration_file_line_change
        )
        self.node_set.lnd_node.configuration.line_change.connect(
            self.handle_configuration_file_line_change
        )

        self.table.cellChanged.connect(self.handle_cell_change)

    def handle_configuration_file_line_change(self, node_name: str, key: str,
                                              new_value: str):
        row_number = self.table.rowCount()
        self.table.insertRow(row_number)
        for column_index, cell_text in enumerate([node_name, key, new_value]):
            item = QTableWidgetItem()
            item.setText(cell_text)
            if column_index != 2:
                item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(row_number, column_index, item)
        self.table.resizeColumnsToContents()

    def handle_cell_change(self, row: int, column: int):
        if column != 2:
            return

        key_item = self.table.item(row, 1)
        if key_item is not None:
            key = key_item.text()
        else:
            return
        value_key_items = self.table.findItems(key, Qt.MatchExactly)
        value_items = [self.table.item(i.row(), 2) for i in value_key_items]
        new_values = [i.text() for i in value_items]

        node_name = self.table.item(row, 0).text()
        if node_name == 'bitcoind':
            config = self.node_set.bitcoind_node.configuration
        elif node_name == 'lnd':
            config = self.node_set.lnd_node.configuration
        elif node_name == 'tor':
            config = self.node_set.tor_node.configuration
        else:
            raise NotImplementedError(f'{node_name} does not exist')

        old_values = [l[1] for l in config.lines if l[0] == key]
        print('here')