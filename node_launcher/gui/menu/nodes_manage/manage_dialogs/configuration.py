from typing import List, Tuple, Optional

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QGridLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox

# A row is represented by a tuple with the first element being the index
# and the second element being the list of column values
Row = Tuple[int, List[str]]


class ConfigurationDialog(QDialog):

    def __init__(self, node):
        super().__init__()

        self.node = node

        self.delete_popup = None

        self.layout = QGridLayout()

        self.table = QTableWidget(0, 2)
        self.node.configuration.parameter_change.connect(
            self.handle_configuration_change
        )

        self.table.cellChanged.connect(self.handle_cell_change)
        self.table.setHorizontalHeaderLabels(['Key', 'Value'])

        self.layout.addWidget(self.table, 0, 0, 1, 2)

        self.deleteButton = QPushButton('Remove Selected Row')
        self.deleteButton.clicked.connect(
            self.handle_delete_action
        )
        self.layout.addWidget(self.deleteButton, 1, 0)

        self.addButton = QPushButton('Add Configuration')
        self.addButton.clicked.connect(
            self.handle_add_action
        )
        self.layout.addWidget(self.addButton, 1, 1)

        self.setLayout(self.layout)

    #################################
    # Add/Update/Get for table rows #
    #################################

    def add_row(self, key, value):
        """
        Adds a new row with key and value.

        :param key: Key for the new row
        :param value: Value for the new row
        :return: None
        """

        row_index = self.table.rowCount()
        self.table.insertRow(row_index)
        self.update_row(row_index, key, value)

    def update_row(self, row_index, key, value):
        """
        Updates a table row by index, with key and value.

        :param row_index: Index of the row to be updated
        :param key: Key for that row
        :param value: Value for that row
        :return: None
        """

        # Disconnecting cellChanged event so we don't get a feedback loop
        self.table.cellChanged.disconnect()

        for column_index, cell_text in enumerate([key, value]):
            item = QTableWidgetItem()
            item.setText(str(cell_text))

            if column_index != 1:
                # noinspection PyUnresolvedReferences
                item.setFlags(Qt.ItemIsEnabled)

            self.table.setItem(row_index, column_index, item)

        # Connecting the cellChanged event again
        self.table.cellChanged.connect(self.handle_cell_change)

        self.table.resizeColumnsToContents()

    def remove_row(self, row_index):
        row: Row = self.get_row_by_index(row_index)
        key = row[1][0]
        value = row[1][1]

        old_values = self.node.configuration[key]
        if old_values is None:
            old_values = []
        elif not isinstance(old_values, list):
            old_values = [old_values]

        new_values = []
        for old_value in old_values:
            if str(old_value) != str(value):
                new_values.append(old_value)

        if key in self.node.configuration:
            del self.node.configuration[key]

        self.node.configuration[key] = new_values

        # The event triggered by configuration values changing will update the table

    def get_rows_by_key(self, key: str) -> List[Row]:
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
            _key = self.table.item(row_index, 0).text() if self.table.item(row_index, 0) else ''
            if _key == key:
                rows.append(
                    (row_index, [
                        self.table.item(row_index, column_index).text()
                        if self.table.item(row_index, column_index) else ''
                        for column_index in range(self.table.columnCount())
                    ])
                )

        return rows

    def get_row_by_index(self, index: int) -> Optional[Row]:
        """
        Returns a row by its index, or None if it doesn't exist.

        :param index: index of the row to retrieve
        :return: If the row doesn't exist, returns None
        If the row exists, returns a tuple with the row number and the list of columns
        Example: (1, ['server', '1'])
        """

        for row_index in range(self.table.rowCount()):
            if row_index == index:
                return (row_index, [
                    self.table.item(row_index, column_index).text() if self.table.item(row_index, column_index) else ''
                    for column_index in range(self.table.columnCount())
                ])

        return None

    ##################
    # Event Handlers #
    ##################

    def handle_configuration_change(self, _: str, key: str, values: List[str]):
        """
        Handles the event of a configuration change and updates the table.
        There's a complication here because a single key can have multiple values, for parameters like
        'addnode' or 'connect' on bitcoind. So we need to handle them all.

        :param _: The name of the node. (bitcoind, lnd, tor). Unused here.
        :param key: Which key was updated
        :param values: All values for that key.
        :return: None
        """

        if not isinstance(values, list):
            values = [values]

        # Deleting extra existing rows
        old_rows: List[Row] = self.get_rows_by_key(key)
        delete_rows_count = len(old_rows) - len(values)
        if delete_rows_count > 0:
            # In this case there's more rows in the table than should exist
            for old_row in reversed(old_rows):
                if delete_rows_count == 0:
                    break

                self.table.removeRow(old_row[0])
                delete_rows_count -= 1

        # Adding new rows
        add_rows_count = len(values) - len(old_rows)
        if add_rows_count > 0:
            # In this case there's less rows in the table than should exist
            for i in range(add_rows_count):
                new_value = values[len(old_rows) + i]
                self.add_row(key, new_value)

        # Updating rows
        update_values = values[0:min(len(values), len(old_rows))]
        for old_row_index, update_value in enumerate(update_values):
            row_index = old_rows[old_row_index][0]
            self.update_row(row_index, key, update_value)

    def handle_cell_change(self, row_index: int, column_index: int):
        """
        Handles the event of a cell value change in the UI.
        Updates the configuration assuming that it is valid.
        Otherwise just keeps what was there before

        :param row_index: Index of the row that changed
        :param column_index: Index of the column that changed
        :return: None
        """

        if column_index == 0:
            row: Row = self.get_row_by_index(row_index)
            key = row[1][0]
            if key == '':
                self.table.removeRow(row_index)
        elif column_index == 1:
            row: Row = self.get_row_by_index(row_index)
            new_value = row[1][1]
            key = row[1][0]

            rows = self.get_rows_by_key(key)
            new_values = sorted([row[1][1] for row in rows])

            old_values = self.node.configuration[key]
            if old_values is None:
                old_values = []
            elif not isinstance(old_values, list):
                old_values = [old_values]

            old_values.sort()

            if [str(e) for e in old_values] != [str(e) for e in new_values]:
                is_valid = self.node.configuration.is_valid_configuration(key, new_value) and key != ''
                if is_valid:
                    if key in self.node.configuration:
                        del self.node.configuration[key]
                    self.node.configuration[key] = new_values
                else:
                    if key == '':
                        self.table.removeRow(row_index)
                    else:
                        for old_value in old_values:
                            if old_value not in new_values:
                                self.update_row(row_index, key, old_value)
                                break

    def handle_confirm_deletion(self):
        self.node.configuration.parameter_change.disconnect()

        items = list(self.table.selectedItems())

        for i, item in enumerate(items):
            if i == len(items) - 1:
                self.node.configuration.parameter_change.connect(
                    self.handle_configuration_change
                )
            self.remove_row(item.row())

        self.delete_popup = None

    def handle_delete_action(self):
        keys = []
        for item in list(self.table.selectedItems()):
            row: Row = self.get_row_by_index(item.row())
            keys.append(row[1][0])

        if keys:
            self.delete_popup = QMessageBox()
            self.delete_popup.setWindowTitle('Confirm deletion')
            self.delete_popup.setText('Are you sure you want to delete ' + ', '.join(keys) + '?')
            self.delete_popup.show()
            self.delete_popup.buttonClicked.connect(self.handle_confirm_deletion)

    def handle_add_action(self):
        row_index = self.table.rowCount()
        self.table.insertRow(row_index)
