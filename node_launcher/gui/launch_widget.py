from PySide2 import QtWidgets

from node_launcher.gui.network_group_box import NetworkGroupBox


class LaunchWidget(QtWidgets.QWidget):
    def __init__(self, node_launcher):
        super().__init__()
        self.node_launcher = node_launcher
        self.grid = QtWidgets.QGridLayout()
        self.testnet_group_box = NetworkGroupBox('testnet', self.node_launcher)
        self.mainnet_group_box = NetworkGroupBox('mainnet', self.node_launcher)
        self.grid.addWidget(self.testnet_group_box, 1, 1)
        self.grid.addWidget(self.mainnet_group_box, 1, 2)
        self.setLayout(self.grid)
