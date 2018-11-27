from PySide2 import QtWidgets
from PySide2.QtWidgets import QErrorMessage

from node_launcher.gui.image_label import ImageLabel
from node_launcher.node_launcher import NodeLauncher, BitcoinNotInstalledException


class NetworkGroupBox(QtWidgets.QGroupBox):
    def __init__(self, group_name: str, node_launcher: NodeLauncher):
        super().__init__(group_name)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(ImageLabel(f'bitcoin-{group_name}.png'))
        layout.addStretch(1)

        self.bitcoin_qt_button = QtWidgets.QPushButton('Bitcoin')
        bitcoin_qt_launcher = getattr(node_launcher, f'{group_name}_bitcoin_qt_node')
        self.bitcoin_qt_button.clicked.connect(lambda: self.on_click(bitcoin_qt_launcher))
        layout.addWidget(self.bitcoin_qt_button)

        self.lnd_button = QtWidgets.QPushButton('LND')
        lnd_launcher = getattr(node_launcher, f'{group_name}_lnd_node')
        self.lnd_button.clicked.connect(lnd_launcher)
        layout.addWidget(self.lnd_button)

        self.setLayout(layout)

    def on_click(self, fn):
        try:
            fn()
        except BitcoinNotInstalledException:
            error_message = QErrorMessage(self)
            error_message.showMessage('Please install Bitcoin https://bitcoincore.org/en/download/')
