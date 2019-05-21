from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QCheckBox,
    QLabel,
    QPushButton,
    QWidget
)

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.horizontal_line import HorizontalLine
from node_launcher.gui.components.selectable_text import SelectableText
from .bitcoind_restart_layout import BitcoindRestartLayout
from node_launcher.gui.utilities import reveal
from .data_directories import DataDirectoryBox

from node_launcher.node_set.bitcoind.bitcoind_node import BitcoindNode


class BitcoindConfigurationTab(QWidget):
    def __init__(self, bitcoind_node: BitcoindNode):
        super().__init__()

        self.bitcoind_node = bitcoind_node

        self.layout = QGridLayout()

        self.bitcoin_version = SelectableText(
            f'Bitcoin Core '
            f'version {self.bitcoind_node.software.release_version}'
        )
        self.layout.addWidget(self.bitcoin_version)

        self.data_directory_group_box = DataDirectoryBox(
            bitcoin_node=self.bitcoind_node)
        self.data_directory_group_box.file_dialog.new_data_directory.connect(
            self.change_datadir
        )
        self.layout.addWidget(self.data_directory_group_box)
        self.layout.setAlignment(self.data_directory_group_box, Qt.AlignHCenter)

        self.enable_wallet_label = QLabel('Enable wallet')
        self.enable_wallet_widget = QCheckBox('Enable Wallet')
        self.enable_wallet_widget.stateChanged.connect(
            lambda x: self.set_conf_value('disablewallet', not bool(x))
        )
        self.layout.addWidget(self.enable_wallet_widget)

        self.layout.addWidget(HorizontalLine())

        self.restart_layout = BitcoindRestartLayout(bitcoin=self.bitcoind_node)
        self.layout.addLayout(self.restart_layout)

        self.show_bitcoin_conf = QPushButton('Show bitcoin.conf')
        self.show_bitcoin_conf.clicked.connect(
            lambda: reveal(self.bitcoind_node.configuration.file.path)
        )
        self.layout.addWidget(self.show_bitcoin_conf)

        self.setLayout(self.layout)

    def change_datadir(self, new_datadir: str):
        self.bitcoind_node.file['datadir'] = new_datadir
        self.bitcoind_node.set_prune()
        self.data_directory_group_box.set_datadir(
            self.bitcoind_node.file['datadir'],
            self.bitcoind_node.file['prune']
        )

    @staticmethod
    def set_checked(widget: QCheckBox, state: bool):
        if state is None:
            widget.setChecked(False)
            return
        widget.setChecked(state)

    def set_conf_value(self, key: str, new_value):
        self.bitcoind_node.file[key] = new_value
