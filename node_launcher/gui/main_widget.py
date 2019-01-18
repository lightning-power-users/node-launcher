import sys

from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMessageBox, QErrorMessage, QVBoxLayout, \
    QLineEdit, QApplication, QMainWindow

from node_launcher.constants import (
    MAINNET,
    NODE_LAUNCHER_RELEASE,
    TESTNET,
    UPGRADE
)
from node_launcher.exceptions import ZmqPortsNotOpenError
from node_launcher.gui.components.tabs import Tabs
from node_launcher.gui.data_directory.data_directory_box import DataDirectoryBox
from node_launcher.gui.network_buttons.network_widget import NetworkWidget
from node_launcher.services.launcher_software import LauncherSoftware


class MainWidget(QtWidgets.QWidget):
    data_directory_group_box: DataDirectoryBox
    error_message: QErrorMessage
    grid: QVBoxLayout
    mainnet_network_widget: NetworkWidget
    network_grid: Tabs
    testnet_network_widget: NetworkWidget

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Node Launcher')
        self.message_box = QMessageBox(self)
        self.message_box.setTextFormat(Qt.RichText)
        self.error_message = QErrorMessage(self)
        try:
            self.mainnet_network_widget = NetworkWidget(network=MAINNET)
            self.testnet_network_widget = NetworkWidget(network=TESTNET)
        except ZmqPortsNotOpenError as e:
            self.error_message.showMessage(str(e))
            self.error_message.exec_()
            sys.exit(0)

        self.data_directory_group_box = DataDirectoryBox()
        self.data_directory_group_box.file_dialog.new_data_directory.connect(
            self.change_datadir
        )
        self.data_directory_group_box.set_datadir(
            self.mainnet_network_widget.node_set.bitcoin.file['datadir'],
            self.mainnet_network_widget.node_set.bitcoin.file['prune']
        )

        self.network_grid = Tabs(
            self,
            mainnet=self.mainnet_network_widget,
            testnet=self.testnet_network_widget
        )

        self.tab_widgets = [self.mainnet_network_widget, self.testnet_network_widget]

        self.mainnet_network_widget.start_refresh_timer()
        self.network_grid.currentChanged.connect(self.on_tab_change)

        self.grid = QVBoxLayout()
        self.grid.addStretch()
        self.grid.addWidget(self.data_directory_group_box)
        self.grid.addWidget(self.network_grid)
        self.grid.setAlignment(self.data_directory_group_box, Qt.AlignHCenter)
        self.setLayout(self.grid)

        self.check_version()

    def on_tab_change(self, i):
        for index, tab_widget in enumerate(self.tab_widgets):
            if index == i:
                tab_widget.start_refresh_timer()
            else:
                tab_widget.stop_refresh_timer()

    def check_version(self):
        latest_version = LauncherSoftware().get_latest_release_version()
        latest_major, latest_minor, latest_bugfix = latest_version.split('.')
        major, minor, bugfix = NODE_LAUNCHER_RELEASE.split('.')

        major_upgrade = latest_major > major

        minor_upgrade = (latest_major == major
                         and latest_minor > minor)

        bugfix_upgrade = (latest_major == major
                          and latest_minor == minor
                          and latest_bugfix > bugfix)

        if major_upgrade or minor_upgrade or bugfix_upgrade:
            self.message_box.setText(UPGRADE)
            self.message_box.setInformativeText(
                f'Your version: {NODE_LAUNCHER_RELEASE}\n'
                f'New version: {latest_version}'
            )
            self.message_box.exec_()

    def change_datadir(self, new_datadir: str):
        self.mainnet_network_widget.node_set.bitcoin.file['datadir'] = new_datadir
        self.testnet_network_widget.node_set.bitcoin.file['datadir'] = new_datadir
        self.mainnet_network_widget.node_set.bitcoin.set_prune()
        self.testnet_network_widget.node_set.bitcoin.set_prune()
        self.data_directory_group_box.set_datadir(
            self.mainnet_network_widget.node_set.bitcoin.file['datadir'],
            self.mainnet_network_widget.node_set.bitcoin.file['prune']
        )

    def mousePressEvent(self, event):
        focused_widget = QApplication.focusWidget()
        if isinstance(focused_widget, QLineEdit):
            focused_widget.clearFocus()
        QMainWindow.mousePressEvent(self, event)
