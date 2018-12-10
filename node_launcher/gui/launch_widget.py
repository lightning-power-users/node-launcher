from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QMessageBox

from node_launcher.constants import NODE_LAUNCHER_RELEASE, UPGRADE
from node_launcher.gui.data_directory import DataDirectoryBox
from node_launcher.gui.network_group_box import NetworkGroupBox
from node_launcher.services.launcher_software import LauncherSoftware


class LaunchWidget(QtWidgets.QWidget):
    mainnet_group_box: NetworkGroupBox
    testnet_group_box: NetworkGroupBox
    network_grid: QGridLayout

    def __init__(self):
        super().__init__()
        self.message_box = QMessageBox(self)
        self.message_box.setTextFormat(Qt.RichText)

        self.testnet_group_box = NetworkGroupBox('testnet')
        self.mainnet_group_box = NetworkGroupBox('mainnet')
        self.data_directory_group_box = DataDirectoryBox(self.mainnet_group_box.node_set)

        self.network_grid = QtWidgets.QGridLayout()
        self.network_grid.addWidget(self.testnet_group_box, 1, 1)
        self.network_grid.addWidget(self.mainnet_group_box, 1, 2)

        self.grid = QtWidgets.QVBoxLayout()
        self.grid.addStretch()
        self.grid.addWidget(self.data_directory_group_box)
        self.grid.addLayout(self.network_grid)
        self.grid.setAlignment(self.data_directory_group_box, Qt.AlignHCenter)
        self.setLayout(self.grid)

        latest_version = LauncherSoftware().get_latest_release_version()
        if latest_version != NODE_LAUNCHER_RELEASE:
            self.message_box.setText(UPGRADE)
            self.message_box.setInformativeText(
                f'Your version: {NODE_LAUNCHER_RELEASE}\n'
                f'New version: {latest_version}'
            )
            self.message_box.exec_()
