from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QMessageBox

from node_launcher.constants import NODE_LAUNCHER_RELEASE, UPGRADE
from node_launcher.gui.advertisement_label import AdvertisementLabel
from node_launcher.gui.data_directory import DataDirectoryBox
from node_launcher.gui.network_group_box import NetworkGroupBox
from node_launcher.lnd_client.lnd_client import LndClient
from node_launcher.node_launcher import NodeLauncher
from node_launcher.node_software.launcher_software import LauncherSoftware


class LaunchWidget(QtWidgets.QWidget):
    mainnet_group_box: NetworkGroupBox
    testnet_group_box: NetworkGroupBox
    grid: QGridLayout
    node_launcher: NodeLauncher
    lnd_client = LndClient

    def __init__(self, node_launcher: NodeLauncher):
        super().__init__()
        self.node_launcher = node_launcher
        self.message_box = QMessageBox(self)
        self.message_box.setTextFormat(Qt.RichText)

        self.advertisement_label = AdvertisementLabel(self)
        self.data_directory_group_box = DataDirectoryBox(self.node_launcher.command_generator)
        self.testnet_group_box = NetworkGroupBox('testnet', self.node_launcher)
        self.mainnet_group_box = NetworkGroupBox('mainnet', self.node_launcher)

        self.grid = QtWidgets.QGridLayout()
        self.grid.addWidget(self.advertisement_label, 1, 1, 1, 2)
        self.grid.addWidget(self.data_directory_group_box, 2, 1, 1, 2)
        self.grid.addWidget(self.testnet_group_box, 3, 1)
        self.grid.addWidget(self.mainnet_group_box, 3, 2)
        self.setLayout(self.grid)

        latest_version = LauncherSoftware().get_latest_release_version()
        if latest_version != NODE_LAUNCHER_RELEASE:
            self.message_box.setText(UPGRADE)
            self.message_box.setInformativeText(
                f'Your version: {NODE_LAUNCHER_RELEASE}\n'
                f'New version: {latest_version}'
            )
            self.message_box.exec_()
