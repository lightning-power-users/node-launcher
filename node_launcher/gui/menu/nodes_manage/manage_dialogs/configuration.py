
from node_launcher.gui.qt import Qt, QDialog, QGridLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox

from node_launcher.node_set.lib.configuration import ConfigurationProperty

from node_launcher.node_set.lib.network_node import NetworkNode

# noinspection PyUnresolvedReferences
editDisabledFlags = Qt.ItemFlags() ^ Qt.ItemIsEnabled


class ConfigurationDialog(QDialog):

    def __init__(self, node):
        super().__init__()

        self.node: NetworkNode = node

        self.delete_popup = None

        self.layout = QGridLayout()

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(['Id', 'Key', 'Value'])

        self.table.setColumnHidden(0, True)

        self.node.configuration.configuration_changed.connect(
            self.handle_configuration_change
        )

        self.table.cellChanged.connect(self.handle_cell_change)

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

    def add_row(self, key, value, identifier):
        """
        Adds a new row with key and value.

        :param key: Key for the new row
        :param value: Value for the new row
        :param identifier: Identifier for the new row
        :return: None
        """

        row_index = self.table.rowCount()
        self.table.insertRow(row_index)
        self.update_row(key, value, identifier=identifier, row_index=row_index)

    def update_row(self, key, value, identifier=None, row_index=None):
        """
        Updates a table row by row index or identifier, with key and value.

        :param key: Key for that row
        :param value: Value for that row
        :param identifier: identifier of the row to be updated
        :param row_index: Index of the row to be updated
        :return: None
        """

        if identifier is None and row_index is None:
            return

        # Disconnecting cellChanged event so we don't get a feedback loop
        self.table.cellChanged.disconnect()

        if row_index is not None:
            for column_index, cell_text in enumerate([identifier, key, value]):
                item = QTableWidgetItem()
                item.setText(str(cell_text) if cell_text is not None else '')

                if column_index != 2:
                    item.setFlags(editDisabledFlags)

                self.table.setItem(row_index, column_index, item)
        elif identifier is not None:
            for row_index in range(self.table.rowCount()):
                row_identifier = self.table.item(row_index, 0).text()
                if row_identifier == identifier:
                    key_item = QTableWidgetItem()
                    key_item.setText(key)
                    key_item.setFlags(editDisabledFlags)
                    value_item = QTableWidgetItem()
                    value_item.setText(str(value))
                    self.table.setItem(row_index, 1, key_item)
                    self.table.setItem(row_index, 2, value_item)
                    break

        # Connecting the cellChanged event again
        self.table.cellChanged.connect(self.handle_cell_change)

        self.table.resizeColumnsToContents()

    def remove_row(self, row_index):
        tableItem = self.table.item(row_index, 0)
        if tableItem is not None:
            identifier = self.table.item(row_index, 0).text()

            if identifier:
                self.node.configuration.remove_configuration_by_identifier(identifier, signal=False)

        self.table.removeRow(row_index)

    ##################
    # Event Handlers #
    ##################

    def handle_configuration_change(self, old_value: ConfigurationProperty, new_value: ConfigurationProperty):
        """
        Handles the event of a configuration change and updates the table.

        :param old_value: Previous value for this configuration
        :param new_value: New value for this configuration
        :return: None
        """

        if new_value is not None:
            if old_value is not None:
                self.update_row(new_value.name, new_value.value, identifier=old_value.identifier)
            else:
                self.add_row(new_value.name, new_value.value, new_value.identifier)
        else:
            for row_index in range(self.table.rowCount()):
                row_identifier = self.table.item(row_index, 0).text()
                if row_identifier == old_value.identifier:
                    self.table.removeRow(row_index)

    def handle_cell_change(self, row_index: int, column_index: int):
        """
        Handles the event of a cell value change in the UI.
        Updates the configuration assuming that it is valid.
        Otherwise just keeps what was there before

        :param row_index: Index of the row that changed
        :param column_index: Index of the column that changed
        :return: None
        """

        key = self.table.item(row_index, 1).text()
        if key == '':
            self.table.removeRow(row_index)
            return

        if column_index == 2:

            identifier = self.table.item(row_index, 0).text()
            key = self.table.item(row_index, 1).text()
            value = self.table.item(row_index, 2).text()

            if identifier:
                old_configuration: ConfigurationProperty = self.node.configuration.get_configuration_by_identifier(identifier)
                new_configuration: ConfigurationProperty = self.node.configuration.edit_configuration(identifier, value, signal=False)
                if new_configuration is None:
                    self.update_row(old_configuration.name, old_configuration.value, identifier=old_configuration.identifier)
            else:
                configuration: ConfigurationProperty = self.node.configuration.append_configuration(key, value, signal=False)
                self.table.item(row_index, 0).setText(configuration.identifier)
                self.table.item(row_index, 0).setFlags(editDisabledFlags)
                self.table.item(row_index, 1).setFlags(editDisabledFlags)

    def handle_confirm_deletion(self):
        items = list(self.table.selectedItems())

        for i, item in enumerate(items):
            self.remove_row(item.row())

        self.delete_popup = None

    def handle_delete_action(self):
        keys = []
        for item in list(self.table.selectedItems()):
            keys.append(self.table.item(item.row(), 1).text())

        if keys:
            self.delete_popup = QMessageBox()
            self.delete_popup.setWindowTitle('Confirm deletion')
            self.delete_popup.setText('Are you sure you want to delete ' + ', '.join(keys) + '?')
            self.delete_popup.show()
            self.delete_popup.buttonClicked.connect(self.handle_confirm_deletion)

    def handle_add_action(self):

        self.table.cellChanged.disconnect()

        row_index = self.table.rowCount()
        self.table.insertRow(row_index)
        identifierItem = QTableWidgetItem()
        identifierItem.setFlags(editDisabledFlags)
        self.table.setItem(row_index, 0, identifierItem)

        self.table.cellChanged.connect(self.handle_cell_change)
