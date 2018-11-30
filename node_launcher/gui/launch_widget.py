from PySide2 import QtWidgets
from PySide2.QtWidgets import QGridLayout

from node_launcher.gui.advertisement_label import AdvertisementLabel
from node_launcher.gui.data_directory import DataDirectoryBox
from node_launcher.gui.horizontal_line import HorizontalLine
from node_launcher.gui.network_group_box import NetworkGroupBox
from node_launcher.node_launcher import NodeLauncher


class LaunchWidget(QtWidgets.QWidget):
    mainnet_group_box: NetworkGroupBox
    testnet_group_box: NetworkGroupBox
    grid: QGridLayout
    node_launcher: NodeLauncher

    def __init__(self, node_launcher: NodeLauncher):
        super().__init__()
        self.node_launcher = node_launcher

        self.advertisement_label = AdvertisementLabel(self)
        self.data_directory_group_box = DataDirectoryBox(self.node_launcher.command_generator)
        self.testnet_group_box = NetworkGroupBox('testnet', self.node_launcher)
        self.mainnet_group_box = NetworkGroupBox('mainnet', self.node_launcher)

        self.grid = QtWidgets.QGridLayout()
        self.grid.addWidget(self.advertisement_label, 1, 1, 1, 2)
        self.grid.addWidget(self.data_directory_group_box, 2, 1, 1, 2)
        self.grid.addWidget(self.testnet_group_box, 3, 1)
        self.grid.addWidget(self.mainnet_group_box, 3, 2)
        self.setLayout(self.grid)
