from node_launcher.gui.components.copy_button import CopyButton
from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.network_buttons.section_name import SectionName
from node_launcher.node_set import NodeSet


class CliLayout(QGridLayout):
    copy_lncli: CopyButton
    copy_bitcoin_cli: CopyButton
    node_set: NodeSet

    def __init__(self, node_set: NodeSet):
        super(CliLayout, self).__init__()
        self.node_set = node_set
        self.copy_bitcoin_cli = CopyButton(
            button_text='bitcoin-cli',
            copy_text=self.node_set.bitcoin.bitcoin_cli
        )
        self.copy_lncli = CopyButton(
            button_text='lncli',
            copy_text=self.node_set.lnd.lncli
        )
        columns = 2

        self.addWidget(SectionName('Command Line'), column_span=columns)
        self.addLayout(self.copy_bitcoin_cli)
        self.addLayout(self.copy_lncli, same_row=True, column=columns)
