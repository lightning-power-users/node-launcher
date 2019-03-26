from PySide2 import QtCore
from PySide2.QtCore import QCoreApplication, Slot
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QApplication, QWidget

from node_launcher.assets.asset_access import asset_access
from node_launcher.gui.menu import Menu
from node_launcher.gui.network_buttons.advanced import AdvancedWidget
from node_launcher.gui.network_buttons.bitcoind_output_widget import \
    BitcoindOutputWidget
from node_launcher.gui.network_buttons.lnd_output_widget import LndOutputWidget
from node_launcher.gui.settings.settings_tab_dialog import SettingsTabDialog
from node_launcher.gui.system_tray import SystemTray
from node_launcher.node_set import NodeSet


class Application(QApplication):
    def __init__(self):
        super().__init__()

        self.node_set = NodeSet()

        path = asset_access.get_asset_full_path('system_tray_icon_red.png')
        pixmap = QPixmap(path)
        icon = QIcon(pixmap)

        self.parent = QWidget()
        self.parent.hide()
        self.parent.setWindowFlags(self.parent.windowFlags() & ~QtCore.Qt.Tool)

        self.system_tray = SystemTray(icon, self.parent)
        self.menu = Menu()
        self.lnd_output_widget = LndOutputWidget(self.node_set)
        self.bitcoind_output_widget = BitcoindOutputWidget(
            self.node_set
        )

        # bitcoind output
        self.node_set.bitcoin.process.readyReadStandardError.connect(
            self.bitcoind_output_widget.handle_error
        )
        self.node_set.bitcoin.process.readyReadStandardOutput.connect(
            self.bitcoind_output_widget.handle_output
        )
        self.menu.bitcoind_output_action.triggered.connect(self.bitcoind_output_widget.show)

        # lnd output
        self.node_set.lnd.process.readyReadStandardError.connect(
            self.lnd_output_widget.handle_error
        )
        self.node_set.lnd.process.readyReadStandardOutput.connect(
            self.lnd_output_widget.handle_output
        )
        self.menu.lnd_output_action.triggered.connect(self.lnd_output_widget.show)

        # advanced

        self.advanced_widget = AdvancedWidget(self.node_set)
        self.menu.advanced_action.triggered.connect(self.advanced_widget.show)

        # quit
        self.menu.quit_action.triggered.connect(self.quit)

        self.system_tray.setContextMenu(self.menu)

        # settings

        self.settings_tab = SettingsTabDialog(node_set=self.node_set)
        self.menu.settings_action.triggered.connect(self.settings_tab.show)

        self.setQuitOnLastWindowClosed(False)

        self.aboutToQuit.connect(self.quit_app)

        self.system_tray.show()

    @Slot()
    def quit_app(self):
        self.node_set.lnd.process.terminate()
        self.node_set.lnd.process.waitForFinished(2000)
        self.node_set.bitcoin.process.terminate()
        self.node_set.bitcoin.process.waitForFinished(2000)
        self.node_set.bitcoin.process.kill()

        QCoreApplication.exit(0)
