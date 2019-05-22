from unittest.mock import MagicMock, patch
from tempfile import NamedTemporaryFile

import pytest
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest

from node_launcher.constants import TARGET_BITCOIN_RELEASE
from node_launcher.gui.menu.nodes_manage.manage_dialogs.configuration import ConfigurationDialog
from node_launcher.node_set.lib.configuration import Configuration


@pytest.fixture
def configuration_dialog() -> ConfigurationDialog:
    with NamedTemporaryFile(suffix='node.conf', delete=False) as f:
        path = f.name
    configuration = Configuration(name='node', path=path)
    configuration.load()
    node = MagicMock()
    node.configuration = configuration
    # node.software.release_version = TARGET_BITCOIN_RELEASE
    dialog = ConfigurationDialog(node)
    return dialog


class TestConfigurationDialog(object):
    def test_init(self, qtbot, configuration_dialog: ConfigurationDialog):
        assert configuration_dialog

    def test_get_nothing(self, qtbot, configuration_dialog: ConfigurationDialog):
        existing_value_items = configuration_dialog.get_rows_by_key('server')
        assert not existing_value_items

    def test_append_key_value(
            self, qtbot, configuration_dialog: ConfigurationDialog):
        configuration_dialog.add_row(
            'test_key',
            'test_new_value'
        )
        assert configuration_dialog.table.rowCount() == 1
        assert configuration_dialog.table.item(0, 0).text() == 'test_key'
        assert configuration_dialog.table.item(0, 1).text() == 'test_new_value'

    def test_update_key(self, qtbot, configuration_dialog: ConfigurationDialog):
        configuration_dialog.node.configuration.parameter_change.emit(
            'bitcoind', 'testing_key', ['test_value_1', 'test_value_2']
        )
        assert configuration_dialog.table.rowCount() == 2
        assert configuration_dialog.table.item(0, 0).text() == 'testing_key'
        assert configuration_dialog.table.item(0, 1).text() == 'test_value_1'

        assert configuration_dialog.table.item(1, 0).text() == 'testing_key'
        assert configuration_dialog.table.item(1, 1).text() == 'test_value_2'

    def test_handle_cell_change(self, qtbot,
                                configuration_dialog: ConfigurationDialog):
        configuration_dialog.add_row(
            'test_key',
            'test_new_value'
        )
        configuration_dialog.table.item(0, 1).setText('test_edit_value')
        assert configuration_dialog.node.configuration['test_key'] == 'test_edit_value'

        configuration_dialog.add_row(
            'test_key',
            'test_new_value2'
        )
        configuration_dialog.table.item(1, 1).setText('test_edit_multi_value')
        assert sorted(configuration_dialog.node.configuration['test_key']) == sorted([
            'test_edit_value',
            'test_edit_multi_value'
        ])
