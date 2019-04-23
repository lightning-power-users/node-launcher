from PySide2.QtCore import Qt
from PySide2.QtWidgets import QVBoxLayout

from node_launcher.gui.components.output_widget import OutputWidget
from node_launcher.gui.components.tabs_dialog import TabsDialog
from .bitcoind_configuration_tab import BitcoindConfigurationTab
from node_launcher.constants import BITCOIN_CLI_COMMANDS
from node_launcher.gui.components.console_dialog import ConsoleWidget
from node_launcher.node_set.bitcoind.bitcoind_node import BitcoindNode


class BitcoindManagerTabsDialog(TabsDialog):
    def __init__(self, bitcoind_node: BitcoindNode, system_tray):
        super().__init__()

        self.bitcoind_node = bitcoind_node
        self.system_tray = system_tray

        # bitcoin console
        self.console_tab = ConsoleWidget(
            title='bitcoin-cli',
            program=self.bitcoind_node.software.bitcoin_cli,
            args=self.bitcoind_node.configuration.args,
            commands=BITCOIN_CLI_COMMANDS
        )
        self.tab_widget.addTab(self.console_tab, 'bitcoin-cli')

        self.output_tab = OutputWidget()
        self.bitcoind_node.process.log_line.connect(
            self.output_tab.output_text_edit.append
        )
        self.tab_widget.addTab(self.output_tab, 'Logs')

        self.configuration_tab = BitcoindConfigurationTab(self.bitcoind_node)
        self.tab_widget.addTab(self.configuration_tab, 'Configuration')

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tab_widget)
        self.setLayout(self.main_layout)

        self.setWindowTitle('Manage Bitcoin')

        self.has_run_help = False

    def show(self):
        super().showMaximized()

        self.configuration_tab.data_directory_group_box.set_datadir(
            self.bitcoind_node.file['datadir'],
            self.bitcoind_node.file['prune']
        )

        self.console_tab.input.setFocus()
        self.raise_()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
        if not self.has_run_help:
            self.console_tab.run_command('help')
