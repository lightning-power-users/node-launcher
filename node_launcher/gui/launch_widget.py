import sys

from PySide2 import QtWidgets
from PySide2.QtCore import Qt, QTimer
from PySide2.QtWidgets import QGridLayout, QMessageBox, QErrorMessage

from node_launcher.constants import NODE_LAUNCHER_RELEASE, UPGRADE, \
    OPERATING_SYSTEM, LINUX
from node_launcher.exceptions import ZmqPortsNotOpenError
from node_launcher.gui.components.tabs import Tabs
from node_launcher.gui.data_directory import DataDirectoryBox
from node_launcher.gui.network_buttons import NetworkWidget
from node_launcher.services.launcher_software import LauncherSoftware


class LaunchWidget(QtWidgets.QWidget):
    error_message: QErrorMessage
    network_grid: QGridLayout
    mainnet_group_box: NetworkWidget
    testnet_group_box: NetworkWidget

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Node Launcher')
        self.message_box = QMessageBox(self)
        self.error_message = QErrorMessage(self)
        self.message_box.setTextFormat(Qt.RichText)
        try:
            self.testnet_group_box = NetworkWidget(network='testnet',
                                                   parent=self)
            self.mainnet_group_box = NetworkWidget(network='mainnet',
                                                   parent=self)
        except ZmqPortsNotOpenError as e:
            self.error_message.showMessage(str(e))
            self.error_message.exec_()
            sys.exit(0)

        self.data_directory_group_box = DataDirectoryBox(
            self.mainnet_group_box.node_set)

        self.network_grid = Tabs(mainnet=self.mainnet_group_box,
                                 testnet=self.testnet_group_box)

        self.grid = QtWidgets.QVBoxLayout()
        self.grid.addStretch()
        self.grid.addWidget(self.data_directory_group_box)
        self.grid.addWidget(self.network_grid)
        self.grid.setAlignment(self.data_directory_group_box, Qt.AlignHCenter)
        self.setLayout(self.grid)

        latest_version = LauncherSoftware().get_latest_release_version()
        latest_major, latest_minor, latest_bugfix = latest_version.split('.')
        major, minor, bugfix = NODE_LAUNCHER_RELEASE.split('.')
        major_upgrade = latest_major > major
        minor_upgrade = latest_major == major and latest_minor > minor
        bugfix_upgrade = latest_major == major and latest_minor == minor and latest_bugfix > bugfix
        if major_upgrade or minor_upgrade or bugfix_upgrade:
            self.message_box.setText(UPGRADE)
            self.message_box.setInformativeText(
                f'Your version: {NODE_LAUNCHER_RELEASE}\n'
                f'New version: {latest_version}'
            )
            self.message_box.exec_()
