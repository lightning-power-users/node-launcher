from PySide2 import QtWidgets


class LaunchWidget(QtWidgets.QWidget):
    def __init__(self, node_launcher):
        super().__init__()
        self.node_launcher = node_launcher

        self.launchTestnetBitcoinQtNodeButton = QtWidgets.QPushButton("Launch testnet Bitcoin node")
        self.launchTestnetLndNodeButton = QtWidgets.QPushButton("Launch testnet LND node")
        self.launchMainnetBitcoinQtNodeButton = QtWidgets.QPushButton("Launch mainnet Bitcoin node")

        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(self.launchTestnetBitcoinQtNodeButton)
        self.layout.addWidget(self.launchTestnetLndNodeButton)
        self.layout.addWidget(self.launchMainnetBitcoinQtNodeButton)

        self.setLayout(self.layout)

        self.launchTestnetBitcoinQtNodeButton.clicked.connect(self.node_launcher.launchTestnetBitcoinQtNode)
        self.launchTestnetLndNodeButton.clicked.connect(self.node_launcher.launchTestnetLndNode)
        self.launchMainnetBitcoinQtNodeButton.clicked.connect(self.node_launcher.launchMainnetBitcoinQtNode)
