from typing import List, Tuple, Optional

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QGridLayout, QTableWidget, QTableWidgetItem


# TODO: handle multiple values for the same key
# connect=123.123.123.123
# connect=124.124.124.124

class ConfigurationDialog(QDialog):

    def __init__(self, node):
        super().__init__()

        self.node = node

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.table = QTableWidget(0, 2)
        self.node.configuration.parameter_change.connect(
            self.handle_configuration_change
        )

        self.table.cellChanged.connect(self.handle_cell_change)

        self.layout.addWidget(self.table)

        self.table.setHorizontalHeaderLabels(['Key', 'Value'])

    def update_row(self, row_index, key, value):
        for column_index, cell_text in enumerate([key, value]):
            item = QTableWidgetItem()
            item.setText(str(cell_text))
            if column_index != 1:
                # noinspection PyUnresolvedReferences
                item.setFlags(Qt.ItemIsEnabled)
            self.table.cellChanged.disconnect()
            self.table.setItem(row_index, column_index, item)
            self.table.cellChanged.connect(self.handle_cell_change)
        self.table.resizeColumnsToContents()

    def get_rows_by_key(self, key: str) -> List[Tuple[int, List[str]]]:
        """
        Returns the list of rows for a specific key. Since we can have multiple values for the same key
        we need to return a list of rows.
        :param key: The key we're looking for
        :return: The list of rows in the format:
        [
            (row_index, [column0value, column1value, ...]),
            ...
        ]
        """
        rows = []
        for row_index in range(self.table.rowCount()):
            _key = self.table.item(row_index, 0).text()
            if _key == key:
                rows.append(
                    (row_index, [
                        self.table.item(row_index, column_index).text()
                        for column_index in range(self.table.columnCount())
                    ])
                )

        return rows

    def get_row_by_index(self, index: int) -> Optional[Tuple[int, List[str]]]:
        """
        Returns a row by its index, or null if it doesn't exist
        :param index: index of the row to retrieve
        :return: If the row doesn't exist, returns None
        If the row exists, returns a tuple with the row number and the list of columns
        Example: (1, ['server', '1'])
        """
        for row_index in range(self.table.rowCount()):
            if row_index == index:
                return (row_index, [
                    self.table.item(row_index, column_index).text()
                    for column_index in range(self.table.columnCount())
                ])

        return None

    def handle_configuration_change(self, _: str, key: str, values: List[str]):
        """
        Deals with the event of a configuration change and updates the table.
        There's a complication here because a single key can have multiple values, for parameters like
        'addnode' or 'connect' on bitcoind. So we need to handle them all.
        :param _: The name of the node. (bitcoind, lnd, tor). Unused here.
        :param key: Which key was updated
        :param values: All values for that key.
        :return: None
        """
        if not isinstance(values, list):
            values = [values]

        old_rows = self.get_rows_by_key(key)
        delete_rows_count = len(old_rows) - len(values)
        if delete_rows_count > 0:
            # In this case there's more rows in the table than should exist
            for row in reversed(old_rows):


        if row is None:
            row_number = self.table.rowCount()
            self.table.insertRow(row_number)
            self.update_row(row_number, key, value)
        else:
            self.update_row(row[0], key, row[1][1])

    def handle_cell_change(self, row_index: int, column_index: int):
        if column_index == 1:
            row = self.get_row_by_index(row_index)
            if row is not None:
                key = row[1][0]
                value = row[1][1]
                old_values = [l[1] for l in self.node.configuration.lines if l[0] == key]
                if old_values != [value]:
                    is_valid = self.node.configuration.is_valid_configuration(key, value)
                    if is_valid:
                        self.node.configuration[key] = [value]
                    else:
                        self.update_row(row_index, key, old_values[0])
