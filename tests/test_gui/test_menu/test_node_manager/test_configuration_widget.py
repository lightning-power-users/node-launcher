from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock

import pytest

from node_launcher.gui.menu.node_manager.configuration_widget import \
    ConfigurationWidget
from node_launcher.node_set.lib.configuration import Configuration


@pytest.fixture
def configuration_widget():
    with NamedTemporaryFile(suffix='.conf', delete=True) as f:
        name = f.name
    configuration = Configuration('bitcoind', name)
    configuration.load()
    node_set = MagicMock()
    node_set.bitcoind_node.configuration = configuration
    widget = ConfigurationWidget(node_set)
    return widget


class TestConfigurationWidget(object):
    def test_init(self, qtbot, configuration_widget: ConfigurationWidget):
        assert configuration_widget.table

    def test_handle_configuration_file_line_change(
            self, qtbot, configuration_widget: ConfigurationWidget):
        configuration_widget.handle_configuration_file_line_change(
            'bitcoind',
            'test_key',
            'test_new_value'
        )
        assert configuration_widget.table.rowCount() == 1
        assert configuration_widget.table.item(0, 0).text() == 'bitcoind'
        assert configuration_widget.table.item(0, 1).text() == 'test_key'
        assert configuration_widget.table.item(0, 2).text() == 'test_new_value'

    def test_handle_cell_change(self, qtbot,
                                configuration_widget: ConfigurationWidget):
        # configuration_widget.handle_configuration_file_line_change(
        #     'bitcoind',
        #     'test_key',
        #     'test_new_value'
        # )
        assert configuration_widget.node_set.bitcoind_node.configuration['test_key'] == ['test_new_value']
