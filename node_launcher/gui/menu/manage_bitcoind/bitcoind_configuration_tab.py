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
from .bitcoind_ports_layout import BitcoindPortsLayout
from .bitcoind_restart_layout import BitcoindRestartLayout
from node_launcher.gui.utilities import reveal
from .data_directories import DataDirectoryBox

from node_launcher.node_set.bitcoind.bitcoin import Bitcoin


class BitcoindConfigurationTab(QWidget):
    def __init__(self, bitcoin: Bitcoin):
        super().__init__()

        self.bitcoin = bitcoin

        self.layout = QGridLayout()

        self.bitcoin_version = SelectableText(
            f'Bitcoin Core '
            f'version {self.bitcoin.software.release_version}'
        )
        self.layout.addWidget(self.bitcoin_version)

        self.data_directory_group_box = DataDirectoryBox(bitcoin=self.bitcoin)
        self.data_directory_group_box.file_dialog.new_data_directory.connect(
            self.change_datadir
        )
        self.layout.addWidget(self.data_directory_group_box)
        self.layout.setAlignment(self.data_directory_group_box, Qt.AlignHCenter)

        self.enable_wallet_label = QLabel('Enable wallet')
        self.enable_wallet_widget = QCheckBox('Enable Wallet')
        self.enable_wallet_widget.setChecked(not self.bitcoin.file['disablewallet'])
        self.enable_wallet_widget.stateChanged.connect(
            lambda x: self.set_conf_value('disablewallet', not bool(x))
        )
        self.layout.addWidget(self.enable_wallet_widget)

        self.layout.addWidget(HorizontalLine())

        self.ports_layout = BitcoindPortsLayout(bitcoin=self.bitcoin)
        self.layout.addLayout(self.ports_layout)

        self.restart_layout = BitcoindRestartLayout(bitcoin=self.bitcoin)
        self.layout.addLayout(self.restart_layout)

        self.show_bitcoin_conf = QPushButton('Show bitcoin.conf')
        self.show_bitcoin_conf.clicked.connect(
            lambda: reveal(self.bitcoin.file.directory)
        )
        self.layout.addWidget(self.show_bitcoin_conf)

        self.setLayout(self.layout)

    def change_datadir(self, new_datadir: str):
        self.bitcoin.file['datadir'] = new_datadir
        self.bitcoin.set_prune()
        self.data_directory_group_box.set_datadir(
            self.bitcoin.file['datadir'],
            self.bitcoin.file['prune']
        )

    @staticmethod
    def set_checked(widget: QCheckBox, state: bool):
        if state is None:
            widget.setChecked(False)
            return
        widget.setChecked(state)

    def set_conf_value(self, key: str, new_value):
        self.bitcoin.file[key] = new_value
