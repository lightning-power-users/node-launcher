from node_launcher.constants import NODE_LAUNCHER_RELEASE
from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.selectable_text import SelectableText
from node_launcher.node_set import NodeSet


class VersionsLayout(QGridLayout):
    def __init__(self, node_set: NodeSet):
        super(VersionsLayout, self).__init__()
        self.node_set = node_set

        self.columns = 2

        self.node_launcher_version = SelectableText(
            f'Node Launcher version {NODE_LAUNCHER_RELEASE}'
        )

        self.bitcoin_version = SelectableText(
            f'Bitcoin Core '
            f'version {self.node_set.bitcoin.software.release_version}'
        )

        self.lnd_version = SelectableText(
            f'LND '
            f'version {self.node_set.lnd.software.release_version}'
        )

        self.addWidget(self.node_launcher_version, column_span=self.columns)
        self.addWidget(self.bitcoin_version, column_span=self.columns)
        self.addWidget(self.lnd_version, column_span=self.columns)
