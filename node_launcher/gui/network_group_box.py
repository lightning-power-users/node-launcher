from PySide2 import QtWidgets

from node_launcher.gui.image_label import ImageLabel
from node_launcher.node_launcher import NodeLauncher


class NetworkGroupBox(QtWidgets.QGroupBox):
    def __init__(self, group_name: str, node_launcher: NodeLauncher):
        super().__init__(group_name)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(ImageLabel(f'bitcoin-{group_name}.png'))
        layout.addStretch(1)

        self.bitcoin_qt_button = QtWidgets.QPushButton('Bitcoin')
        bitcoin_qt_launcher = getattr(node_launcher, f'{group_name}_bitcoin_qt_node')
        self.bitcoin_qt_button.clicked.connect(bitcoin_qt_launcher)
        layout.addWidget(self.bitcoin_qt_button)

        self.lnd_button = QtWidgets.QPushButton('LND')
        lnd_launcher = getattr(node_launcher, f'{group_name}_lnd_node')
        self.lnd_button.clicked.connect(lnd_launcher)
        layout.addWidget(self.lnd_button)

        self.setLayout(layout)
