from unittest.mock import MagicMock

import pytest

from node_launcher.gui.system_tray_widgets import AdvancedWidget


@pytest.fixture
def advanced_widget():
    node_set = MagicMock()
    advanced_widget = AdvancedWidget(node_set)
    return advanced_widget


class TestAdvancedWidget(object):
    pass
