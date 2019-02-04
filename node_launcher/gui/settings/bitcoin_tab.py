from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QLabel, QCheckBox, QVBoxLayout

from node_launcher.gui.settings.data_directories.data_directory_box import \
    DataDirectoryBox
from node_launcher.node_set.bitcoin import Bitcoin


class BitcoinTab(QWidget):
    def __init__(self, bitcoin: Bitcoin):
        super().__init__()

        self.bitcoin = bitcoin

        self.bitcoin_layout = QVBoxLayout()

        self.data_directory_group_box = DataDirectoryBox()
        self.data_directory_group_box.file_dialog.new_data_directory.connect(
            self.change_datadir
        )
        self.data_directory_group_box.set_datadir(
            self.bitcoin.file['datadir'],
            self.bitcoin.file['prune']
        )
        self.bitcoin_layout.addWidget(self.data_directory_group_box)
        self.bitcoin_layout.setAlignment(self.data_directory_group_box, Qt.AlignHCenter)

        self.enable_wallet_label = QLabel('Enable wallet')
        self.enable_wallet_widget = QCheckBox('Enable Wallet')
        self.enable_wallet_widget.setChecked(not self.bitcoin.file['disablewallet'])
        self.enable_wallet_widget.stateChanged.connect(self.enable_wallet)
        self.bitcoin_layout.addWidget(self.enable_wallet_widget)
        self.setLayout(self.bitcoin_layout)

    def change_datadir(self, new_datadir: str):
        self.bitcoin.file['datadir'] = new_datadir
        self.bitcoin.set_prune()
        self.data_directory_group_box.set_datadir(
            self.bitcoin.file['datadir'],
            self.bitcoin.file['prune']
        )

    def enable_wallet(self, state: int):
        self.bitcoin.file['disablewallet'] = not bool(state)
