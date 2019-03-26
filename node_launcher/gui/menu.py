from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QMenu


class Menu(QMenu):
    def __init__(self):
        super().__init__()

        self.bitcoind_output_action = self.addAction('See Bitcoin Output')

        self.lnd_output_action = self.addAction('See LND Output')

        self.addSeparator()

        self.settings_action = self.addAction('&Settings')
        self.settings_action.setShortcut(QKeySequence.Preferences)
        self.advanced_action = self.addAction('Advanced...')

        self.addSeparator()

        self.quit_action = self.addAction('Quit')
