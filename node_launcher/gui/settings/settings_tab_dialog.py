from PySide2.QtWidgets import QDialog, QTabWidget, QDialogButtonBox, QVBoxLayout

from node_launcher.gui.settings.bitcoin_tab import BitcoinTab
from node_launcher.gui.settings.lnd_tab import LndTab
from node_launcher.node_set import NodeSet


class SettingsTabDialog(QDialog):
    def __init__(self, node_set: NodeSet, parent=None):
        super().__init__(parent=parent)
        self.node_set = node_set
        self.tab_widget = QTabWidget()

        self.bitcoin_tab = BitcoinTab(self.node_set.bitcoin)
        self.tab_widget.addTab(self.bitcoin_tab, 'Bitcoin')

        self.lnd_tab = LndTab(self.node_set.lnd)
        self.tab_widget.addTab(self.lnd_tab, 'LND')

        self.button_box = QDialogButtonBox()
        self.button_box.addButton('Ok', QDialogButtonBox.AcceptRole)

        self.button_box.accepted.connect(self.accept)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tab_widget)
        self.main_layout.addWidget(self.button_box)
        self.setLayout(self.main_layout)

        self.setWindowTitle('Settings')
