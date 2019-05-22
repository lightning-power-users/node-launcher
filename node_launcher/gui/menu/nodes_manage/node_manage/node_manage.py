
from PySide2.QtWidgets import QTabWidget, QDialog, QGridLayout

from node_launcher.gui.menu.nodes_manage.node_manage.node_manage_configuration import node_tabs

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

        self.tab_dialogs = []

        for node_tab in node_tabs[self.network]:
            tab_dialog = node_tab['class'](self.node)
            self.tabs.addTab(tab_dialog, node_tab['title'])
