from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QTabWidget, QDialogButtonBox, QVBoxLayout

from .bitcoind_output_tab import BitcoindOutputTab
from .bitcoind_console_tab import BitcoindConsoleTab


class BitcoindManagerTabsDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.tab_widget = QTabWidget()

        # bitcoin console
        self.bitcoin_cli_widget = ConsoleDialog(
            title='bitcoin-cli',
            program=self.node_set.bitcoin.software.bitcoin_cli,
            args=self.node_set.bitcoin.args,
            commands=BITCOIN_CLI_COMMANDS
        )


        self.bitcoind_output_widget = BitcoindOutputWidget(
            node_set=self.node_set,
            system_tray=self.system_tray
        )
        
        self.bitcoind_output_tab = BitcoindOutputTab()
        self.tab_widget.addTab(self.bitcoin_output_tab, 'Logs')

        self.bitcoind_console_tab = BitcoindConsoleTab()
        self.tab_widget.addTab(self.lnd_tab, 'Console')

        self.bitcoin_tab = BitcoindConfigurationTab(self.node_set.bitcoin)
        self.tab_widget.addTab(self.bitcoin_tab, 'Configuration')

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tab_widget)
        self.setLayout(self.main_layout)

        self.setWindowTitle('Manage Bitcoin')

    def show(self):
        super().show()
        self.raise_()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
