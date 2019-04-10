from PySide2.QtCore import Qt
from PySide2.QtWidgets import QVBoxLayout

from node_launcher.gui.components.tabs_dialog import TabsDialog
from .bitcoind_configuration_tab import BitcoindConfigurationTab
from .bitcoind_output_tab import BitcoindOutputTab
from node_launcher.constants import BITCOIN_CLI_COMMANDS
from node_launcher.gui.components.console_dialog import ConsoleWidget
from node_launcher.node_set.bitcoin import Bitcoin


class BitcoindManagerTabsDialog(TabsDialog):
    def __init__(self, bitcoin: Bitcoin, system_tray):
        super().__init__()

        self.bitcoin = bitcoin
        self.system_tray = system_tray

        # bitcoin console
        self.console_tab = ConsoleWidget(
            title='bitcoin-cli',
            program=self.bitcoin.software.bitcoin_cli,
            args=self.bitcoin.args,
            commands=BITCOIN_CLI_COMMANDS
        )
        self.tab_widget.addTab(self.console_tab, 'bitcoin-cli')

        self.output_tab = BitcoindOutputTab(
            bitcoin=self.bitcoin,
            system_tray=self.system_tray
        )
        self.tab_widget.addTab(self.output_tab, 'Logs')

        self.configuration_tab = BitcoindConfigurationTab(self.bitcoin)
        self.tab_widget.addTab(self.configuration_tab, 'Configuration')

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tab_widget)
        self.setLayout(self.main_layout)

        self.setWindowTitle('Manage Bitcoin')

        self.has_run_help = False

    def show(self):
        super().show()

        self.configuration_tab.data_directory_group_box.set_datadir(
            self.bitcoin.file['datadir'],
            self.bitcoin.file['prune']
        )

        self.console_tab.input.setFocus()
        self.raise_()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()

        if not self.has_run_help:
            self.console_tab.run_command('help')
