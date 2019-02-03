from PySide2.QtWidgets import QWidget, QLabel, QCheckBox, QVBoxLayout

from node_launcher.node_set.bitcoin import Bitcoin


class BitcoinTab(QWidget):
    def __init__(self, bitcoin: Bitcoin):
        super().__init__()

        self.bitcoin = bitcoin
        self.enable_wallet_label = QLabel('Enable wallet')
        self.enable_wallet_widget = QCheckBox('Enable Wallet')
        self.enable_wallet_widget.setChecked(not self.bitcoin.file['disablewallet'])
        self.enable_wallet_widget.stateChanged.connect(self.test)
        self.bitcoin_layout = QVBoxLayout()
        self.bitcoin_layout.addWidget(self.enable_wallet_widget)
        self.setLayout(self.bitcoin_layout)

    def test(self, state: int):
        self.bitcoin.file['disablewallet'] = not bool(state)
