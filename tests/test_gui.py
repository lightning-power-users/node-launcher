from unittest.mock import MagicMock

from PySide2.QtCore import Qt

from node_launcher.gui.launch_widget import LaunchWidget


def test_launchTestnetBitcoinQtNodeButton_works(qtbot):
    node_launcher = MagicMock()
    node_launcher.launchTestnetBitcoinQtNode = MagicMock(return_value=None)
    launch_widget = LaunchWidget(node_launcher)
    qtbot.mouseClick(launch_widget.launchTestnetBitcoinQtNodeButton, Qt.LeftButton)
    node_launcher.launchTestnetBitcoinQtNode.assert_called_once()
