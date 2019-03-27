from PySide2.QtCore import QCoreApplication
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QSystemTrayIcon, QWidget

from node_launcher.assets.asset_access import asset_access
from node_launcher.constants import BITCOIN_CLI_COMMANDS, LNCLI_COMMANDS
from node_launcher.gui.cli.cli import CliWidget
from node_launcher.gui.menu import Menu
from node_launcher.gui.network_buttons.advanced import AdvancedWidget
from node_launcher.gui.network_buttons.bitcoind_output_widget import \
    BitcoindOutputWidget
from node_launcher.gui.network_buttons.lnd_output_widget import LndOutputWidget
from node_launcher.gui.settings.settings_tab_dialog import SettingsTabDialog
from node_launcher.node_set import NodeSet


class SystemTray(QSystemTrayIcon):
    def __init__(self, parent: QWidget, node_set: NodeSet):
        super(SystemTray, self).__init__(parent=parent)
        self.node_set = node_set
        self.set_red()
        self.menu = Menu()



        # bitcoind output
        self.bitcoind_output_widget = BitcoindOutputWidget(
            node_set=self.node_set,
            system_tray=self
        )
        self.node_set.bitcoin.process.readyReadStandardError.connect(
            self.bitcoind_output_widget.handle_error
        )
        self.node_set.bitcoin.process.readyReadStandardOutput.connect(
            self.bitcoind_output_widget.handle_output
        )
        self.menu.bitcoind_output_action.triggered.connect(
            self.bitcoind_output_widget.show
        )

        # bitcoin console
        self.bitcoin_cli_widget = CliWidget(
            title='bitcoin-cli',
            program=self.node_set.bitcoin.software.bitcoin_cli,
            args=self.node_set.bitcoin.args,
            commands=BITCOIN_CLI_COMMANDS
        )
        self.menu.bitcoin_console_action.triggered.connect(
            self.bitcoin_cli_widget.show
        )

        # lnd output
        self.lnd_output_widget = LndOutputWidget(
            node_set=self.node_set,
            system_tray=self
        )
        self.node_set.lnd.process.readyReadStandardError.connect(
            self.lnd_output_widget.handle_error
        )
        self.node_set.lnd.process.readyReadStandardOutput.connect(
            self.lnd_output_widget.handle_output
        )
        self.menu.lnd_output_action.triggered.connect(
            self.lnd_output_widget.show
        )
        # lnd console

        self.lncli_widget = CliWidget(
            title='lncli',
            program=self.node_set.lnd.software.lncli,
            args=self.node_set.lnd.lncli_arguments(),
            commands=LNCLI_COMMANDS
        )
        self.menu.lnd_console_action.triggered.connect(
            self.lncli_widget.show
        )

        # advanced

        self.advanced_widget = AdvancedWidget(self.node_set)
        self.menu.advanced_action.triggered.connect(self.advanced_widget.show)

        # quit
        self.menu.quit_action.triggered.connect(lambda _: QCoreApplication.exit(0))

        self.setContextMenu(self.menu)

        # settings

        self.settings_tab = SettingsTabDialog(node_set=self.node_set)
        self.menu.settings_action.triggered.connect(self.settings_tab.show)

    def set_icon(self, color: str):
        path = asset_access.get_asset_full_path(f'system_tray_icon_{color}.png')
        pixmap = QPixmap(path)
        icon = QIcon(pixmap)
        self.setIcon(icon)

    def set_red(self):
        self.set_icon('red')

    def set_orange(self):
        self.set_icon('orange')

    def set_green(self):
        self.set_icon('green')
