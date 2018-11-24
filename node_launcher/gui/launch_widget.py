from PySide2 import QtWidgets


class LaunchWidget(QtWidgets.QWidget):
    def __init__(self, node_launcher):
        super().__init__()
        self.node_launcher = node_launcher

        self.launchTestnetBitcoinQtNodeButton = QtWidgets.QPushButton('Launch testnet Bitcoin')
        self.launchTestnetLndNodeButton = QtWidgets.QPushButton('Launch testnet LND')
        self.launchMainnetBitcoinQtNodeButton = QtWidgets.QPushButton('Launch mainnet Bitcoin')
        self.launchMainnetLndNodeButton = QtWidgets.QPushButton('Launch mainnet LND')

        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(self.launchTestnetBitcoinQtNodeButton)
        self.layout.addWidget(self.launchTestnetLndNodeButton)
        self.layout.addWidget(self.launchMainnetBitcoinQtNodeButton)
        self.layout.addWidget(self.launchMainnetLndNodeButton)

        self.setLayout(self.layout)

        self.launchTestnetBitcoinQtNodeButton.clicked.connect(self.node_launcher.launchTestnetBitcoinQtNode)
        self.launchTestnetLndNodeButton.clicked.connect(self.node_launcher.launchTestnetLndNode)
        self.launchMainnetBitcoinQtNodeButton.clicked.connect(self.node_launcher.launchMainnetBitcoinQtNode)
        self.launchMainnetLndNodeButton.clicked.connect(self.node_launcher.launchMainnetLndNode)
