
from node_launcher.gui.qt import Qt, QTabWidget, QDialog, QVBoxLayout

from node_launcher.node_set import NodeSet

from .node_manage.node_manage import NodeManageDialog


class NodesManageDialog(QDialog):

    def __init__(self, node_set: NodeSet, system_tray):
        # noinspection PyUnresolvedReferences
        super().__init__(
            # f=Qt.WindowMinimizeButtonHint|Qt.WindowMaximizeButtonHint|Qt.WindowCloseButtonHint
        )

        # Dialog properties
        self.setWindowTitle('Manage Nodes')
        self.setMinimumSize(1200, 800)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Locally storing provided parameters
        self.node_set = node_set
        self.system_tray = system_tray

        # Initializing the main tabs widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Initializing tor tab
        self.tor_tab = NodeManageDialog(self.node_set.tor_node)
        self.tabs.addTab(self.tor_tab, 'Tor')

        # Initializing bitcoind tab
        if self.node_set.bitcoind_node:
            self.bitcoind_tab = NodeManageDialog(self.node_set.bitcoind_node)
            self.tabs.addTab(self.bitcoind_tab, 'Bitcoind')

        # Initializing lnd tab
        self.lnd_tab = NodeManageDialog(self.node_set.lnd_node)
        self.tabs.addTab(self.lnd_tab, 'Lnd')

    def show(self):
        super().show()

        self.showMaximized()
        self.raise_()
        self.activateWindow()
