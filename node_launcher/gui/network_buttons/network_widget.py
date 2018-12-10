from PySide2 import QtWidgets
from PySide2.QtWidgets import QWidget

from node_launcher.gui.components.layouts import QGridLayout
from node_launcher.gui.network_buttons.cli_layout import CliLayout
from node_launcher.gui.network_buttons.joule_layout import JouleLayout
from node_launcher.gui.network_buttons.lnd_wallet_layout import \
    LndWalletLayout
from node_launcher.gui.network_buttons.nodes_layout import NodesLayout
from node_launcher.gui.network_buttons.zap_layout import ZapLayout
from node_launcher.node_set import NodeSet


class NetworkWidget(QtWidgets.QWidget):
    node_set: NodeSet

    def __init__(self, parent: QWidget, network: str = 'mainnet'):
        super().__init__()

        self.node_set = NodeSet(network)

        columns = 2

        layout = QGridLayout()
        self.nodes_layout = NodesLayout(node_set=self.node_set)
        layout.addLayout(self.nodes_layout, column_span=columns)

        self.lnd_wallet_layout = LndWalletLayout(node_set=self.node_set,
                                                 parent=parent)
        layout.addLayout(self.lnd_wallet_layout, column_span=columns)

        self.zap_layout = ZapLayout(node_set=self.node_set)
        layout.addLayout(self.zap_layout, column_span=columns)

        self.joule_layout = JouleLayout(node_set=self.node_set)
        layout.addLayout(self.joule_layout, column_span=columns)

        self.cli_layout = CliLayout(node_set=self.node_set)
        layout.addLayout(self.cli_layout, column_span=columns)

        self.setLayout(layout)
