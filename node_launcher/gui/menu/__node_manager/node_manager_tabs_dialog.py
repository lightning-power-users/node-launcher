from PySide2.QtCore import Qt
from PySide2.QtWidgets import QVBoxLayout, QTabWidget, QDialog

from node_launcher.gui.components.output_widget import OutputWidget
from node_launcher.gui.menu.node_manager.configuration_widget import \
    ConfigurationWidget
from node_launcher.gui.menu.node_manager.console_widget import ConsoleWidget
from node_launcher.node_set import NodeSet


class NodeManagerTabsDialog(QDialog):
    def __init__(self, node_set: NodeSet, system_tray):
        super().__init__()

        self.tab_widget = QTabWidget()

        self.tab_widget.currentChanged.connect(
            self.tab_changed_event
        )

        self.node_set = node_set
        self.system_tray = system_tray

        self.console_tab = ConsoleWidget(node_set=self.node_set)
        self.tab_widget.addTab(self.console_tab, 'Console')

        self.output_tab = OutputWidget()
        self.node_set.tor_node.process.log_line.connect(
            lambda line: self.output_tab.append('tor', line)
        )
        self.node_set.bitcoind_node.process.log_line.connect(
            lambda line: self.output_tab.append('bitcoind', line)
        )
        self.node_set.lnd_node.process.log_line.connect(
            lambda line: self.output_tab.append('lnd', line)
        )
        self.tab_widget.addTab(self.output_tab, 'Logs')

        self.configuration_tab = ConfigurationWidget(node_set=node_set)
        self.tab_widget.addTab(self.configuration_tab, 'Configuration')

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tab_widget)
        self.setLayout(self.main_layout)

        self.setWindowTitle('Manage Nodes')

        self.has_run_help = False

    def tab_changed_event(self, tab_index: int):
        if tab_index == 0:
            self.console_tab.input.setFocus()

    def show(self):
        super().showMaximized()

        self.console_tab.input.setFocus()
        self.raise_()
        self.setWindowState(
            self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
        if not self.has_run_help:
            self.console_tab.run_command('help')
