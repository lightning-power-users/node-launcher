from unittest.mock import MagicMock

import pytest

from node_launcher.gui.menu.node_manager.configuration_widget import \
    ConfigurationWidget


@pytest.fixture
def configuration_widget():
    node_set = MagicMock()
    node_set.bitcoind_node.configuration.lines = []
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
