
from PySide2.QtWidgets import QTabWidget, QDialog, QGridLayout

from node_launcher.gui.menu.nodes_manage.manage_dialogs.configuration import ConfigurationDialog
from node_launcher.gui.menu.nodes_manage.manage_dialogs.console import ConsoleDialog
from node_launcher.gui.menu.nodes_manage.manage_dialogs.logs import LogsDialog

from node_launcher.node_set.lib.network_node import NetworkNode


class NodeManageDialog(QDialog):

    def __init__(self, node: NetworkNode):
        super().__init__()

        self.network = node.network
        self.node = node

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Initializing logs tab
        self.logs_tab = LogsDialog(self.node)
        self.tabs.addTab(self.logs_tab, 'Logs')

        # Initializing configuration tab
        self.configuration_tab = ConfigurationDialog(self.node)
        self.tabs.addTab(self.configuration_tab, 'Configuration')

        # Initializing console tab
        if self.network != 'tor':
            self.console_tab = ConsoleDialog(self.node)
            self.tabs.addTab(self.console_tab, 'Console')
