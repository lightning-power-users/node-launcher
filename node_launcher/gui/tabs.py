from PySide2.QtWidgets import QTabWidget

from node_launcher.gui.network_buttons import NetworkWidget


class Tabs(QTabWidget):
    def __init__(self, mainnet: NetworkWidget, testnet: NetworkWidget):
        super(Tabs, self).__init__()
        self.setTabPosition(QTabWidget.North)
        self.addTab(mainnet, 'mainnet')
        self.addTab(testnet, 'testnet')
