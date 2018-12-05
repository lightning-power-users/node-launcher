from unittest.mock import MagicMock

from PySide2.QtCore import Qt
from PySide2.QtTest import QTest

from node_launcher.gui.launch_widget import LaunchWidget


class TestSeedDialog(object):
    def test_show(self, qtbot: QTest, launch_widget: LaunchWidget):
        launch_widget.node_launcher.generate_seed = MagicMock(return_value=['test', 'seed'])

        qtbot.mouseClick(launch_widget.testnet_group_box.initialize_wallet_button,
                         Qt.LeftButton)

