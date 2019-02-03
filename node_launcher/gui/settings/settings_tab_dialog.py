from PySide2.QtWidgets import QDialog, QTabWidget, QDialogButtonBox, QVBoxLayout

from node_launcher.gui.settings.bitcoin_tab import BitcoinTab


class SettingsTabDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.tab_widget = QTabWidget()

        self.bitcoin_tab = BitcoinTab()
        self.tab_widget.addTab(self.bitcoin_tab, 'Bitcoin')

        # self.lnd_tab = LndTab()
        # self.tab_widget.addTab(self.lnd_tab, 'LND')

        self.button_box = QDialogButtonBox()
        self.button_box.addButton('Ok', QDialogButtonBox.AcceptRole)

        self.button_box.accepted.connect(self.accept)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tab_widget)
        self.main_layout.addWidget(self.button_box)
        self.setLayout(self.main_layout)

        self.setWindowTitle('Settings')
