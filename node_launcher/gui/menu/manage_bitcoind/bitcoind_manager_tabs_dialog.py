from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QTabWidget, QVBoxLayout

from node_launcher.constants import BITCOIN_CLI_COMMANDS
from node_launcher.gui.components.console_dialog import ConsoleWidget
from node_launcher.gui.menu.manage_bitcoind.bitcoind_configuration_tab import \
    BitcoindConfigurationTab
from node_launcher.node_set.bitcoin import Bitcoin
from .bitcoind_output_tab import BitcoindOutputTab


class BitcoindManagerTabsDialog(QDialog):
    def __init__(self, bitcoin: Bitcoin, system_tray):
        super().__init__()

        self.bitcoin = bitcoin
        self.system_tray = system_tray

        self.tab_widget = QTabWidget()

        # bitcoin console
        self.bitcoin_cli_tab = ConsoleWidget(
            title='bitcoin-cli',
            program=self.bitcoin.software.bitcoin_cli,
            args=self.bitcoin.args,
            commands=BITCOIN_CLI_COMMANDS
        )
        self.tab_widget.addTab(self.bitcoin_cli_tab, 'bitcoin-cli')

        self.bitcoind_output_tab = BitcoindOutputTab(
            bitcoin=self.bitcoin,
            system_tray=self.system_tray
        )
        self.tab_widget.addTab(self.bitcoin_output_tab, 'Logs')

        self.bitcoin_tab = BitcoindConfigurationTab(self.node_set.bitcoin)
        self.tab_widget.addTab(self.bitcoin_tab, 'Configuration')

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tab_widget)
        self.setLayout(self.main_layout)

        self.setWindowTitle('Manage Bitcoin')

    def show(self):
        super().show()

        self.bitcoin_tab.data_directory_group_box.set_datadir(
            self.node_set.bitcoin.file['datadir'],
            self.node_set.bitcoin.file['prune']
        )

        self.raise_()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
