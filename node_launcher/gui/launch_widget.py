from PySide2 import QtWidgets
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QLabel

from node_launcher.assets.asset_access import AssetAccess


class LaunchWidget(QtWidgets.QWidget):
    def __init__(self, node_launcher, asset_access=AssetAccess()):
        super().__init__()
        self.node_launcher = node_launcher

        self.launchTestnetBitcoinQtNodeButton = QtWidgets.QPushButton('Bitcoin')
        self.launchTestnetLndNodeButton = QtWidgets.QPushButton('LND')
        self.launchMainnetBitcoinQtNodeButton = QtWidgets.QPushButton('Bitcoin')
        self.launchMainnetLndNodeButton = QtWidgets.QPushButton('LND')

        self.grid = QtWidgets.QGridLayout()

        testnet_layout = QtWidgets.QVBoxLayout()
        testnet_image = QLabel(self)
        testnet_pixmap = QPixmap(
            asset_access.get_asset_full_path('bitcoin-testnet.png'))
        testnet_image.setPixmap(testnet_pixmap)
        testnet_layout.addWidget(testnet_image)
        testnet_layout.addWidget(self.launchTestnetBitcoinQtNodeButton)
        testnet_layout.addWidget(self.launchTestnetLndNodeButton)
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
        mainnet_layout.addWidget(self.launchMainnetBitcoinQtNodeButton)
        mainnet_layout.addWidget(self.launchMainnetLndNodeButton)
        mainnet_layout.addStretch(1)
        mainnet_group_box = QtWidgets.QGroupBox('mainnet')
        mainnet_group_box.setLayout(mainnet_layout)
        self.grid.addWidget(mainnet_group_box, 1, 2)

        self.setLayout(self.grid)

        self.launchTestnetBitcoinQtNodeButton.clicked.connect(
            self.node_launcher.launchTestnetBitcoinQtNode)
        self.launchTestnetLndNodeButton.clicked.connect(
            self.node_launcher.launchTestnetLndNode)
        self.launchMainnetBitcoinQtNodeButton.clicked.connect(
            self.node_launcher.launchMainnetBitcoinQtNode)
        self.launchMainnetLndNodeButton.clicked.connect(
            self.node_launcher.launchMainnetLndNode)
