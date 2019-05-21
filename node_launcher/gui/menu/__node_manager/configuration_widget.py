from typing import List, Tuple

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTableWidget, QTableWidgetItem

from node_launcher.node_set import NodeSet


class ConfigurationWidget(QTableWidget):
    def __init__(self, node_set: NodeSet):
        super().__init__(0, 3)
        self.node_set = node_set

        self.node_set.tor_node.configuration.parameter_change.connect(
            self.update_key
        )
        self.node_set.bitcoind_node.configuration.parameter_change.connect(
            self.update_key
        )
        self.node_set.lnd_node.configuration.parameter_change.connect(
            self.update_key
        )

        self.cellChanged.connect(self.handle_cell_change)

        self.setHorizontalHeaderLabels(['Node Name', 'Key', 'Value'])

    def get(self, node_name: str, key: str) -> List[Tuple[int, str]]:
        value_key_items = list(self.findItems(key, Qt.MatchExactly))
        value_items = [(i.row(), self.item(i.row(), 2).text())
                       for i in value_key_items
                       if self.item(i.row(), 0).text() == node_name]
        return value_items

    def append_key_value(self, node_name: str, key: str, new_value: str):
        row_number = self.rowCount()
        self.insertRow(row_number)
        self.update_row(row_number, node_name, key, new_value)

    def update_row(self, row_number, node_name, key, new_value):
        for column_index, cell_text in enumerate([node_name, key, new_value]):
            item = QTableWidgetItem()
            item.setText(cell_text)
            if column_index != 2:
                item.setFlags(Qt.ItemIsEnabled)
            self.cellChanged.disconnect()
            self.setItem(row_number, column_index, item)
            self.cellChanged.connect(self.handle_cell_change)
        self.resizeColumnsToContents()

    def update_key(self, node_name: str, key: str, new_values: List[str]):
        existing_value_items: List[Tuple[int, str]] = self.get(node_name, key)
        if len(existing_value_items) > len(new_values):
            for row_index, _ in existing_value_items:
                self.removeRow(row_index)

        for new_value_index, new_value in enumerate(new_values):
            if new_value_index < len(existing_value_items):
                self.update_row(
                    row_number=existing_value_items[new_value_index][0],
                    node_name=node_name,
                    key=key,
                    new_value=new_value
                )
            elif new_value_index >= len(existing_value_items):
                self.append_key_value(node_name, key, new_value)

    def handle_cell_change(self, row: int, column: int):
        if column == 2:
            self.handle_value_cell_change(row=row)

    def handle_value_cell_change(self, row: int):
        node_name = self.item(row, 0).text()
        key = self.item(row, 1).text()
        new_values = [v[1] for v in self.get(node_name, key)]

        if node_name == 'bitcoind':
            config = self.node_set.bitcoind_node.configuration
        elif node_name == 'lnd':
            config = self.node_set.lnd_node.configuration
        elif node_name == 'tor':
            config = self.node_set.tor_node.configuration
        else:
            raise NotImplementedError(f'{node_name} does not exist')

        old_values = [l[1] for l in config.lines if l[0] == key]
        if sorted(new_values) == sorted(old_values):
            return
        config[key] = new_values
