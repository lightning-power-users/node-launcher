from PySide2.QtWidgets import QPushButton
from PySide2.QtCore import QTimer

from node_launcher.constants import BITCOIN_CLI_COMMANDS, LNCLI_COMMANDS
from node_launcher.gui.cli.cli import CliWidget
from node_launcher.gui.components.copy_button import CopyButton
from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.horizontal_line import HorizontalLine
from node_launcher.gui.components.section_name import SectionName
from node_launcher.node_set import NodeSet


class CliLayout(QGridLayout):
    copy_lncli: CopyButton
    copy_bitcoin_cli: CopyButton
    node_set: NodeSet
    timer = QTimer

    def __init__(self, node_set: NodeSet):
        super(CliLayout, self).__init__()
        self.timer = QTimer(self.parentWidget())
        self.node_set = node_set

        self.lncli_widget = CliWidget(
            title='lncli',
            program=self.node_set.lnd.software.lncli,
            args=self.node_set.lnd.lncli_arguments(),
            commands=LNCLI_COMMANDS
        )

        self.bitcoin_cli_widget = CliWidget(
            title='bitcoin-cli',
            program=self.node_set.bitcoin.software.bitcoin_cli,
            args=self.node_set.bitcoin.args,
            commands=BITCOIN_CLI_COMMANDS
        )

        self.open_bitcoin_cli_button = QPushButton('bitcoin-cli')
        self.open_bitcoin_cli_button.clicked.connect(
            self.bitcoin_cli_widget.show
        )
        self.open_lncli_button = QPushButton('lncli')
        self.open_lncli_button.clicked.connect(
            self.lncli_widget.show
        )

        columns = 2
        self.section_name = SectionName('Command Line')
        self.addWidget(self.section_name, column_span=columns)
        self.addWidget(self.open_bitcoin_cli_button)
        self.addWidget(self.open_lncli_button, same_row=True, column=columns)
        self.horizontal_line = HorizontalLine()
        self.addWidget(self.horizontal_line, column_span=columns)
        self.horizontal_line.hide()
        self.node_set.bitcoin.file.file_watcher.fileChanged.connect(self.check_restart_required)
        self.node_set.lnd.file.file_watcher.fileChanged.connect(self.check_restart_required)
        self.timer.start(1000)
        self.timer.timeout.connect(self.check_restart_required)

    def set_button_state(self):
        self.copy_bitcoin_cli.button.setEnabled(self.node_set.bitcoin.running)
        self.copy_lncli.button.setEnabled(self.node_set.lnd.is_unlocked)

    def check_restart_required(self):
        if self.node_set.bitcoin.restart_required or self.node_set.lnd.restart_required:
            self.horizontal_line.show()
        else:
            self.horizontal_line.hide()
