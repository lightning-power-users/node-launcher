from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QMenu


class Menu(QMenu):
    def __init__(self):
        super().__init__()

        self.bitcoind_status_action = self.addAction('bitcoind off')
        self.bitcoind_status_action.setEnabled(False)
        self.bitcoin_console_action = self.addAction('Open Bitcoin Console')
        self.bitcoind_output_action = self.addAction('See Bitcoin Output')

        self.addSeparator()

        self.lnd_status_action = self.addAction('lnd off')
        self.lnd_status_action.setEnabled(False)
        self.lnd_console_action = self.addAction('Open LND Console')
        self.lnd_output_action = self.addAction('See LND Output')

        self.addSeparator()

        self.settings_action = self.addAction('&Settings')
        self.settings_action.setShortcut(QKeySequence.Preferences)
        self.advanced_action = self.addAction('Advanced...')

        self.addSeparator()

        self.quit_action = self.addAction('Quit')
