from PySide2 import QtCore, QtWidgets, QtGui


class LaunchWidget(QtWidgets.QWidget):
    def __init__(self, node_launcher):
        super().__init__()
        self.node_launcher = node_launcher

        self.launchTestnetBitcoinQtNodeButton = QtWidgets.QPushButton("Launch testnet bitcoin-qt node")
        self.launchMainnetBitcoinQtNodeButton = QtWidgets.QPushButton("Launch mainnet bitcoin-qt node")

        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(self.launchTestnetBitcoinQtNodeButton)
        self.layout.addWidget(self.launchMainnetBitcoinQtNodeButton)

        self.setLayout(self.layout)

        self.launchTestnetBitcoinQtNodeButton.clicked.connect(self.node_launcher.launchTestnetBitcoinQtNode)
        self.launchMainnetBitcoinQtNodeButton.clicked.connect(self.node_launcher.launchMainnetBitcoinQtNode)
