from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QWidget

from node_launcher.constants import MAINNET, Network
from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.node_set import NodeSet
from . import JouleLayout, LndWalletLayout, NodesLayout, ZapLayout


class NetworkWidget(QWidget):
    node_set: NodeSet
    timer = QTimer

    def __init__(self, network: Network = MAINNET):
        super().__init__()

        self.timer = QTimer(self.parentWidget())

        self.node_set = NodeSet(network)

        columns = 2

        layout = QGridLayout()

        self.nodes_layout = NodesLayout(node_set=self.node_set)
        layout.addLayout(self.nodes_layout, column_span=columns)

        self.lnd_wallet_layout = LndWalletLayout(node_set=self.node_set)
        layout.addLayout(self.lnd_wallet_layout, column_span=columns)

        self.zap_layout = ZapLayout(node_set=self.node_set)
        layout.addLayout(self.zap_layout, column_span=columns)

        self.joule_layout = JouleLayout(node_set=self.node_set)
        layout.addLayout(self.joule_layout, column_span=columns)

        self.setLayout(layout)

        self.timer.start(1000)
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.refresh)
        self.refresh()

    def refresh(self):
        self.node_set.bitcoin.check_process()
        self.node_set.lnd.check_process()

        self.nodes_layout.set_button_state()
        self.lnd_wallet_layout.set_button_state()
        self.zap_layout.set_button_state()
        self.joule_layout.set_button_state()
