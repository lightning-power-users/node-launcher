import sys

from PySide2 import QtCore
from PySide2.QtCore import Qt, QTimer, Slot, QCoreApplication
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
    NODE_LAUNCHER_RELEASE,
    UPGRADE,
    Network)
from node_launcher.exceptions import ZmqPortsNotOpenError
from node_launcher.gui.components.tabs import Tabs
from node_launcher.gui.settings.data_directories.data_directory_box import DataDirectoryBox
from node_launcher.gui.network_buttons.network_widget import NetworkWidget
from node_launcher.gui.settings.settings_tab_dialog import SettingsTabDialog
from node_launcher.logging import log
from node_launcher.services.launcher_software import LauncherSoftware


class MainWidget(QWidget):
    data_directory_group_box: DataDirectoryBox
    error_message: QErrorMessage
    grid: QVBoxLayout
    network_grid: Tabs
    network_widget: NetworkWidget
    settings_tab: SettingsTabDialog

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Node Launcher')
        self.error_message = QErrorMessage(self)
        try:
            self.network_widget = NetworkWidget()
        except ZmqPortsNotOpenError as e:
            self.error_message.showMessage(str(e))
            self.error_message.exec_()
            sys.exit(0)

        self.network_grid = Tabs(self, self.network_widget)
        self.network_grid.currentChanged.connect(self.on_tab_change)

        self.grid = QVBoxLayout()

        self.settings_tab = SettingsTabDialog(node_set=self.network_widget.node_set)

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

        self.settings_tab.bitcoin_tab.change_network.connect(self.change_network)

        timer = QTimer()
        timer.singleShot(1000, self.check_version)

    def on_tab_change(self, index: int):
        log.info('on_tab_change', index=index)
        if index == 1:
            self.network_grid.lncli_widget.input.setFocus()
        elif index == 2:
            self.network_grid.bitcoin_cli_widget.input.setFocus()

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

    def change_network(self, network: Network):
        self.network_widget.nodes_layout.image_label.set_image(f'bitcoin-{network}.png')

    def mousePressEvent(self, event):
        focused_widget = QApplication.focusWidget()
        if isinstance(focused_widget, QLineEdit):
            focused_widget.clearFocus()
        QMainWindow.mousePressEvent(self, event)

    def eventFilter(self, obj, event):
        if obj is self and event.type() == QtCore.QEvent.Close:
            self.quit_app()
            event.ignore()
            return True
        return super(MainWidget, self).eventFilter(obj, event)

    @Slot()
    def quit_app(self):
        self.removeEventFilter(self)
        self.network_widget.node_set.lnd.process.terminate()
        self.network_widget.node_set.lnd.process.waitForFinished(2000)
        self.network_widget.node_set.bitcoin.process.terminate()
        self.network_widget.node_set.bitcoin.process.waitForFinished(2000)
        self.network_widget.node_set.bitcoin.process.kill()

        QCoreApplication.exit(0)
