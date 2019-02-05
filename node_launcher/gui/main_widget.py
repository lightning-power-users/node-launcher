import sys

from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    QErrorMessage,
    QLineEdit,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QVBoxLayout,
    QWidget
)

from node_launcher.constants import (
    MAINNET,
    NODE_LAUNCHER_RELEASE,
    TESTNET,
    UPGRADE
)
from node_launcher.exceptions import ZmqPortsNotOpenError
from node_launcher.gui.components.tabs import Tabs
from node_launcher.gui.settings.data_directories.data_directory_box import DataDirectoryBox
from node_launcher.gui.network_buttons.network_widget import NetworkWidget
from node_launcher.gui.settings.settings_tab_dialog import SettingsTabDialog
from node_launcher.services.launcher_software import LauncherSoftware


class MainWidget(QWidget):
    data_directory_group_box: DataDirectoryBox
    error_message: QErrorMessage
    grid: QVBoxLayout
    mainnet_network_widget: NetworkWidget
    network_grid: Tabs
    testnet_network_widget: NetworkWidget

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Node Launcher')
        self.error_message = QErrorMessage(self)
        try:
            self.mainnet_network_widget = NetworkWidget(network=MAINNET)
            self.testnet_network_widget = NetworkWidget(network=TESTNET)
        except ZmqPortsNotOpenError as e:
            self.error_message.showMessage(str(e))
            self.error_message.exec_()
            sys.exit(0)

        self.network_grid = Tabs(
            self,
            mainnet=self.mainnet_network_widget,
            testnet=self.testnet_network_widget
        )

        self.tab_widgets = [self.mainnet_network_widget, self.testnet_network_widget]

        self.mainnet_network_widget.start_refresh_timer()
        self.network_grid.currentChanged.connect(self.on_tab_change)

        self.grid = QVBoxLayout()

        self.settings_tab = SettingsTabDialog(node_set=self.mainnet_network_widget.node_set)

        settings_action = QAction('&Settings', self)
        settings_action.setShortcut(QKeySequence.Preferences)
        settings_action.triggered.connect(self.settings_tab.show)

        self.menubar = QMenuBar()
        self.menubar.setMinimumWidth(self.menubar.sizeHint().width())
        file_menu = self.menubar.addMenu('&File')
        file_menu.addAction(settings_action)
        self.grid.addWidget(self.menubar)

        self.grid.addStretch()
        self.grid.addWidget(self.network_grid)
        self.setLayout(self.grid)

        timer = QTimer()
        timer.singleShot(1000, self.check_version)

    def on_tab_change(self, i):
        for index, tab_widget in enumerate(self.tab_widgets):
            if index == i:
                tab_widget.start_refresh_timer()
            else:
                tab_widget.stop_refresh_timer()

    def check_version(self):
        latest_version = LauncherSoftware().get_latest_release_version()
        if latest_version is None:
            return
        latest_major, latest_minor, latest_bugfix = latest_version.split('.')
        major, minor, bugfix = NODE_LAUNCHER_RELEASE.split('.')

        major_upgrade = latest_major > major

        minor_upgrade = (latest_major == major
                         and latest_minor > minor)

        bugfix_upgrade = (latest_major == major
                          and latest_minor == minor
                          and latest_bugfix > bugfix)

        if major_upgrade or minor_upgrade or bugfix_upgrade:
            message_box = QMessageBox(self)
            message_box.setTextFormat(Qt.RichText)
            message_box.setText(UPGRADE)
            message_box.setInformativeText(
                f'Your version: {NODE_LAUNCHER_RELEASE}\n'
                f'New version: {latest_version}'
            )
            message_box.exec_()

    def mousePressEvent(self, event):
        focused_widget = QApplication.focusWidget()
        if isinstance(focused_widget, QLineEdit):
            focused_widget.clearFocus()
        QMainWindow.mousePressEvent(self, event)
