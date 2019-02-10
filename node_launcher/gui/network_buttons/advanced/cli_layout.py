from node_launcher.gui.components.copy_button import CopyButton
from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.horizontal_line import HorizontalLine
from node_launcher.gui.components.section_name import SectionName
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
        self.section_name = SectionName('Command Line')
        self.addWidget(self.section_name, column_span=columns)
        self.addLayout(self.copy_bitcoin_cli)
        self.addLayout(self.copy_lncli, same_row=True, column=columns)
        self.addWidget(HorizontalLine(), column_span=columns)

    def set_button_state(self):
        self.copy_bitcoin_cli.button.setEnabled(self.node_set.bitcoin.running)
        self.copy_lncli.button.setEnabled(self.node_set.lnd.is_unlocked)
