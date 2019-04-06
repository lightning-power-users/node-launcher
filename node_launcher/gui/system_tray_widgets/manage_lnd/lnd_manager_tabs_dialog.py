from PySide2.QtWidgets import QDialog


class LndManagerTabsDialog(QDialog):
    def __init__(self):
        self.lncli_widget = ConsoleDialog(
            title='lncli',
            program=self.node_set.lnd.software.lncli,
            args=self.node_set.lnd.lncli_arguments(),
            commands=LNCLI_COMMANDS
        )
        self.lnd_console_action = self.addAction('Open LND Console')
        self.lnd_console_action.triggered.connect(
            self.lncli_widget.show
        )

        # lnd output
        self.lnd_output_widget = LndOutputWidget(
            node_set=self.node_set,
            system_tray=self.system_tray
        )
        self.lnd_output_action = self.addAction('See LND Output')
        self.lnd_output_action.triggered.connect(
            self.lnd_output_widget.show
        )
        