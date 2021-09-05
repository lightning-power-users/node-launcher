from unittest.mock import MagicMock
from tempfile import NamedTemporaryFile

import pytest

from node_launcher.gui.menu.nodes_manage.manage_dialogs.configuration import ConfigurationDialog
from node_launcher.node_set.lib.configuration import Configuration
from node_launcher.node_set.lib.configuration_property import ConfigurationProperty


@pytest.fixture
def configuration_dialog() -> ConfigurationDialog:
    with NamedTemporaryFile(suffix='node.conf', delete=False) as f:
        path = f.name
    configuration = Configuration(name='node', path=path)
    configuration.load()
    node = MagicMock()
    node.configuration = configuration
    dialog = ConfigurationDialog(node)
    return dialog


class TestConfigurationDialog(object):
    def test_init(self, configuration_dialog: ConfigurationDialog):
        assert configuration_dialog

    def test_append_key_value(
            self, configuration_dialog: ConfigurationDialog):
        configuration_dialog.add_row(
            'test_key',
            'test_new_value',
            '1'
        )
        assert configuration_dialog.table.rowCount() == 1
        assert configuration_dialog.table.item(0, 0).text() == '1'
        assert configuration_dialog.table.item(0, 1).text() == 'test_key'
        assert configuration_dialog.table.item(0, 2).text() == 'test_new_value'

    def test_update_key(self, configuration_dialog: ConfigurationDialog):
        configuration_dialog.node.configuration.configuration_changed.emit(
            None, ConfigurationProperty('1', 'key', 'value')
        )
        configuration_dialog.node.configuration.configuration_changed.emit(
            None, ConfigurationProperty('2', 'key2', 'value2')
        )

        assert configuration_dialog.table.rowCount() == 2

        assert configuration_dialog.table.item(0, 0).text() == '1'
        assert configuration_dialog.table.item(0, 1).text() == 'key'
        assert configuration_dialog.table.item(0, 2).text() == 'value'

        assert configuration_dialog.table.item(1, 0).text() == '2'
        assert configuration_dialog.table.item(1, 1).text() == 'key2'
        assert configuration_dialog.table.item(1, 2).text() == 'value2'

    def test_handle_cell_change(self,
                                configuration_dialog: ConfigurationDialog):
        configuration_dialog.add_row(
            'test_key',
            'test_new_value',
            ''
        )

        configuration_dialog.table.item(0, 2).setText('test_edit_value')
        assert configuration_dialog.node.configuration['test_key'] == 'test_edit_value'

        configuration_dialog.add_row(
            'test_key',
            'test_new_value2',
            ''
        )
        configuration_dialog.table.item(1, 2).setText('test_edit_multi_value')

        all_config_values = [cp.value for cp in configuration_dialog.node.configuration.get_all_configurations()]

        assert sorted(all_config_values) == sorted([
            'test_edit_value',
            'test_edit_multi_value'
        ])
