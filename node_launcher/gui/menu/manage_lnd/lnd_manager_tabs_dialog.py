from PySide2.QtWidgets import QDialog, QTabWidget

from node_launcher.constants import LNCLI_COMMANDS
from node_launcher.gui.components.console_dialog import ConsoleWidget
from node_launcher.gui.menu import LndOutputWidget


class LndManagerTabsDialog(QDialog):
    def __init__(self, lnd, system_tray):
        super().__init__()

        self.lnd = lnd
        self.system_tray = system_tray

        # lnd console
        self.console_tab = ConsoleWidget(
            title='lncli',
            program=self.lnd.software.lncli,
            args=self.lnd.lncli_arguments(),
            commands=LNCLI_COMMANDS
        )
        self.tab_widget.addTab(self.console_tab, 'lncli')

        # lnd output
        self.lnd_output_widget = LndOutputWidget(
            lnd=self.lnd,
            system_tray=self.system_tray
        )
        self.lnd_output_action = self.addAction('See LND Output')
        self.lnd_output_action.triggered.connect(
            self.lnd_output_widget.show
        )
