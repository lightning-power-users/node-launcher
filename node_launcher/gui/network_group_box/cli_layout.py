from PySide2 import QtWidgets

from node_launcher.gui.components.layouts import QGridLayout
from node_launcher.gui.network_group_box.section_name import SectionName
from node_launcher.gui.utilities import copy_to_clipboard
from node_launcher.node_set import NodeSet


class CliLayout(QGridLayout):
    node_set: NodeSet

    def __init__(self, node_set: NodeSet):
        super(CliLayout, self).__init__()
        self.node_set = node_set
        columns = 2

        self.addWidget(SectionName('Command Line'), column_span=columns)
        # Copy bitcoin-cli command button
        self.bitcoin_cli_copy_button = QtWidgets.QPushButton('bitcoin-cli')
        # noinspection PyUnresolvedReferences
        self.bitcoin_cli_copy_button.clicked.connect(
            lambda: copy_to_clipboard(self.node_set.bitcoin.bitcoin_cli)
        )
        self.addWidget(self.bitcoin_cli_copy_button)

        # Copy lncli command button
        self.lncli_copy_button = QtWidgets.QPushButton('lncli')
        # noinspection PyUnresolvedReferences
        self.lncli_copy_button.clicked.connect(
            lambda: copy_to_clipboard(' '.join(self.node_set.lnd.lncli))
        )
        self.addWidget(self.lncli_copy_button, same_row=True, column=columns)
