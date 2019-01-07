import os

from PySide2 import QtWidgets

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.utilities import reveal
from node_launcher.node_set import NodeSet


class ActionsLayout(QGridLayout):
    node_set: NodeSet

    def __init__(self, node_set: NodeSet):
        super(ActionsLayout, self).__init__()
        self.node_set = node_set
        columns = 2

        self.show_bitcoin_conf = QtWidgets.QPushButton('Show bitcoin.conf')
        bitcoin_conf_dir = os.path.abspath(
            os.path.join(self.node_set.bitcoin.file.path, os.pardir)
        )
        # noinspection PyUnresolvedReferences
        self.show_bitcoin_conf.clicked.connect(
            lambda: reveal(bitcoin_conf_dir)
        )
        self.addWidget(self.show_bitcoin_conf, column=1)

        self.show_lnd_conf = QtWidgets.QPushButton('Show lnd.conf')
        lnd_conf_dir = os.path.abspath(
            os.path.join(self.node_set.lnd.file.path, os.pardir)
        )
        # noinspection PyUnresolvedReferences
        self.show_lnd_conf.clicked.connect(
            lambda: reveal(lnd_conf_dir)
        )
        self.addWidget(self.show_lnd_conf, same_row=True, column=2)
