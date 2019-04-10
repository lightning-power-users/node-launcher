from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import (
    QCheckBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget
)

from node_launcher.constants import Network
from .data_directories import DataDirectoryBox

from node_launcher.node_set.bitcoin import Bitcoin


class BitcoindConfigurationTab(QWidget):
    change_network = Signal(Network)

    def __init__(self, bitcoin: Bitcoin):
        super().__init__()

        self.bitcoin = bitcoin

        self.layout = QVBoxLayout()

        self.show_bitcoin_conf = QPushButton('Show bitcoin.conf')
        # noinspection PyUnresolvedReferences
        self.show_bitcoin_conf.clicked.connect(
            lambda: reveal(self.node_set.bitcoin.file.directory)
        )
        self.layout.addWidget(self.show_bitcoin_conf)

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
            lambda x: self.update_config('disablewallet', not bool(x))
        )
        self.layout.addWidget(self.enable_wallet_widget)

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
