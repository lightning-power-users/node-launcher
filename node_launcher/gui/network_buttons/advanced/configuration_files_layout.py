from PySide2 import QtWidgets

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.section_name import SectionName
from node_launcher.gui.utilities import reveal
from node_launcher.node_set import NodeSet


class ConfigurationFilesLayout(QGridLayout):
    node_set: NodeSet

    def __init__(self, node_set: NodeSet):
        super(ConfigurationFilesLayout, self).__init__()
        self.node_set = node_set

        self.columns = 2

        self.section_name = SectionName('Configuration Files')
        self.addWidget(self.section_name, column_span=self.columns)
        self.show_bitcoin_conf = QtWidgets.QPushButton('Show bitcoin.conf')
        # noinspection PyUnresolvedReferences
        self.show_bitcoin_conf.clicked.connect(
            lambda: reveal(self.node_set.bitcoin.file.directory)
        )
        self.addWidget(self.show_bitcoin_conf)

        self.show_lnd_conf = QtWidgets.QPushButton('Show lnd.conf')
        # noinspection PyUnresolvedReferences
        self.show_lnd_conf.clicked.connect(
            lambda: reveal(self.node_set.lnd.file.directory)
        )
        self.addWidget(self.show_lnd_conf, same_row=True, column=self.columns)
