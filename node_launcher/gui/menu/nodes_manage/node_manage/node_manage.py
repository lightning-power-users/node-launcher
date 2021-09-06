
from node_launcher.gui.qt import QTabWidget, QDialog, QGridLayout

from node_launcher.gui.menu.nodes_manage.node_manage.node_manage_configuration import node_tabs

from node_launcher.node_set.lib.network_node import NetworkNode


class NodeManageDialog(QDialog):

    def __init__(self, node: NetworkNode, parent):
        super().__init__(parent=parent)

        self.network = node.software.node_software_name
        self.node_software_name = node.node_software_name
        self.node = node

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.tab_dialogs = []

        for node_tab in node_tabs[self.node_software_name]:
            tab_dialog = node_tab['class'](self.node)
            self.tabs.addTab(tab_dialog, node_tab['title'])
