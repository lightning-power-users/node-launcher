from PySide2 import QtWidgets
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QLabel

from node_launcher.assets.asset_access import AssetAccess
from node_launcher.node_launcher import NodeLauncher


class LaunchWidget(QtWidgets.QWidget):
    node_launcher: NodeLauncher

    def __init__(self,
                 node_launcher: NodeLauncher,
                 asset_access: AssetAccess = AssetAccess()):
        super().__init__()
        self.node_launcher = node_launcher

        self.testnet_bitcoin_qt_node_button = QtWidgets.QPushButton('Bitcoin')
        self.testnet_lnd_node_button = QtWidgets.QPushButton('LND')
        self.mainnet_bitcoin_qt_node_button = QtWidgets.QPushButton('Bitcoin')
        self.mainnet_lnd_node_button = QtWidgets.QPushButton('LND')

        self.grid = QtWidgets.QGridLayout()

        testnet_layout = QtWidgets.QVBoxLayout()
        testnet_image = QLabel(self)
        testnet_pixmap = QPixmap(
            asset_access.get_asset_full_path('bitcoin-testnet.png'))
        testnet_image.setPixmap(testnet_pixmap)
        testnet_layout.addWidget(testnet_image)
        testnet_layout.addWidget(self.testnet_bitcoin_qt_node_button)
        testnet_layout.addWidget(self.testnet_lnd_node_button)
        testnet_layout.addStretch(1)
        testnet_group_box = QtWidgets.QGroupBox('testnet')
        testnet_group_box.setLayout(testnet_layout)
        self.grid.addWidget(testnet_group_box, 1, 1)

        mainnet_layout = QtWidgets.QVBoxLayout()
        mainnet_image = QLabel(self)
        mainnet_pixmap = QPixmap(
            asset_access.get_asset_full_path('bitcoin.png'))
        mainnet_image.setPixmap(mainnet_pixmap)
        mainnet_layout.addWidget(mainnet_image)
        mainnet_layout.addWidget(self.mainnet_bitcoin_qt_node_button)
        mainnet_layout.addWidget(self.mainnet_lnd_node_button)
        mainnet_layout.addStretch(1)
        mainnet_group_box = QtWidgets.QGroupBox('mainnet')
        mainnet_group_box.setLayout(mainnet_layout)
        self.grid.addWidget(mainnet_group_box, 1, 2)

        self.setLayout(self.grid)

        self.testnet_bitcoin_qt_node_button.clicked.connect(
            self.node_launcher.testnet_bitcoin_qt_node)
        self.testnet_lnd_node_button.clicked.connect(
            self.node_launcher.testnet_lnd_node)
        self.mainnet_bitcoin_qt_node_button.clicked.connect(
            self.node_launcher.mainnet_bitcoin_qt_node)
        self.mainnet_lnd_node_button.clicked.connect(
            self.node_launcher.mainnet_lnd_node)
