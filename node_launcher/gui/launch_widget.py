from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel

from node_launcher.gui.network_group_box import NetworkGroupBox


class LaunchWidget(QtWidgets.QWidget):
    def __init__(self, node_launcher):
        super().__init__()
        self.node_launcher = node_launcher
        self.grid = QtWidgets.QGridLayout()
        self.testnet_group_box = NetworkGroupBox('testnet', self.node_launcher)
        self.mainnet_group_box = NetworkGroupBox('mainnet', self.node_launcher)
        lpu_advertisement = 'Want a real mainnet Bitcoin faucet? Join the ' \
                            '<a href="https://www.lightningpowerusers.com/">Lighting Power Users</a>'
        advertisement_label = QLabel(self)
        advertisement_label.setOpenExternalLinks(True)
        advertisement_label.setFixedHeight(advertisement_label.height() * 2)
        advertisement_label.setText(lpu_advertisement)
        advertisement_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.grid.addWidget(advertisement_label, 1, 1, 1, 2)
        self.grid.addWidget(self.testnet_group_box, 2, 1)
        self.grid.addWidget(self.mainnet_group_box, 2, 2)
        self.setLayout(self.grid)
