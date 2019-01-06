import pytest

from node_launcher.gui.advanced.advanced_widget import AdvancedWidget


@pytest.fixture
def advanced_widget():
    advanced_widget = AdvancedWidget()
    return advanced_widget
