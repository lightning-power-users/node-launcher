from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock

import pytest

from node_launcher.gui.menu.node_manager.configuration_widget import \
    ConfigurationWidget
from node_launcher.node_set.lib.configuration import Configuration


@pytest.fixture
def configuration_widget():
    with NamedTemporaryFile(suffix='.conf', delete=False) as f:
        path = f.name
    configuration = Configuration(name='bitcoind', path=path)
    configuration.load()
    node_set = MagicMock()
    node_set.bitcoind_node.configuration = configuration
    widget = ConfigurationWidget(node_set)
    return widget


class TestConfigurationWidget(object):
    def test_init(self, qtbot, configuration_widget: ConfigurationWidget):
        assert configuration_widget

    def test_get_nothing(self, qtbot, configuration_widget: ConfigurationWidget):
        existing_value_items = configuration_widget.get('bitcoind', 'server')
        assert not existing_value_items

    def test_append_key_value(
            self, qtbot, configuration_widget: ConfigurationWidget):
        configuration_widget.append_key_value(
            'bitcoind',
            'test_key',
            'test_new_value'
        )
        assert configuration_widget.rowCount() == 1
        assert configuration_widget.item(0, 0).text() == 'bitcoind'
        assert configuration_widget.item(0, 1).text() == 'test_key'
        assert configuration_widget.item(0, 2).text() == 'test_new_value'

    def test_update_key(self, qtbot, configuration_widget: ConfigurationWidget):
        configuration_widget.node_set.bitcoind_node.configuration.parameter_change.emit(
            'bitcoind', 'testing_key', ['test_value_1', 'test_value_2']
        )
        assert configuration_widget.rowCount() == 2
        assert configuration_widget.item(0, 0).text() == 'bitcoind'
        assert configuration_widget.item(0, 1).text() == 'testing_key'
        assert configuration_widget.item(0, 2).text() == 'test_value_1'

        assert configuration_widget.item(1, 0).text() == 'bitcoind'
        assert configuration_widget.item(1, 1).text() == 'testing_key'
        assert configuration_widget.item(1, 2).text() == 'test_value_2'

    def test_handle_cell_change(self, qtbot,
                                configuration_widget: ConfigurationWidget):
        configuration_widget.append_key_value(
            'bitcoind',
            'test_key',
            'test_new_value'
        )
        configuration_widget.item(0, 2).setText('test_edit_value')
        assert configuration_widget.node_set.bitcoind_node.configuration['test_key'] == 'test_edit_value'

        configuration_widget.append_key_value(
            'bitcoind',
            'test_key',
            'test_new_value2'
        )
        configuration_widget.item(1, 2).setText('test_edit_multi_value')
        assert configuration_widget.node_set.bitcoind_node.configuration['test_key'] == [
            'test_edit_value',
            'test_edit_multi_value'
        ]
