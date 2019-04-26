from PySide2.QtCore import Qt
from PySide2.QtWidgets import QVBoxLayout

from node_launcher.constants import LNCLI_COMMANDS
from node_launcher.gui.menu.node_manager.console_dialog import ConsoleWidget
from node_launcher.gui.components.output_widget import OutputWidget
from node_launcher.gui.components.tabs_dialog import TabsDialog
from node_launcher.gui.menu.manage_lnd.lnd_configuration_tab import \
    LndConfigurationTab
from node_launcher.node_set.lnd.lnd_node import LndNode


class LndManagerTabsDialog(TabsDialog):
    def __init__(self, lnd_node: LndNode, system_tray):
        super().__init__()

        self.lnd_node = lnd_node
        self.system_tray = system_tray

        # lnd console
        self.console_tab = ConsoleWidget(
            title='lncli',
            software=self.lnd_node.software,
            configuration=self.lnd_node.configuration,
            commands=LNCLI_COMMANDS
        )
        self.tab_widget.addTab(self.console_tab, 'lncli')

        # lnd output
        self.output_tab = OutputWidget()
        self.lnd_node.process.log_line.connect(
            self.output_tab.output_text_edit.append
        )
        self.tab_widget.addTab(self.output_tab, 'Logs')

        self.configuration_tab = LndConfigurationTab(self.lnd_node)
        self.tab_widget.addTab(self.configuration_tab, 'Configuration')

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tab_widget)
        self.setLayout(self.main_layout)

        self.setWindowTitle('Manage LND')

        self.has_run_help = False

    def show(self):
        if self.lnd_node.configuration.file['alias'] is not None:
            self.configuration_tab.alias_layout.set_alias(self.lnd_node.file['alias'])

        super().showMaximized()
        self.raise_()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()

        if not self.has_run_help:
            self.console_tab.run_command('help')
