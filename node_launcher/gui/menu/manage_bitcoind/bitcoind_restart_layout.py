from PySide2.QtCore import QTimer
from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.section_name import SectionName
from node_launcher.node_set import NodeSet
from node_launcher.gui.components.warning_text import WarningText
from node_launcher.node_set.bitcoin import Bitcoin


class BitcoindRestartLayout(QGridLayout):
    bitcoin: Bitcoin
    timer = QTimer

    def __init__(self, bitcoin: Bitcoin):
        super(BitcoindRestartLayout, self).__init__()

        self.timer = QTimer(self.parentWidget())

        self.bitcoin = bitcoin
        columns = 2

        self.section_name = SectionName('Restart Required')
        self.addWidget(self.section_name, column_span=columns)
        self.bitcoin_restart_required = WarningText('Bitcoin: ')
        self.addWidget(self.bitcoin_restart_required)
        self.bitcoin_restart_required.hide()
        self.bitcoin.file.file_watcher.fileChanged.connect(self.check_restart_required)
        self.timer.start(1000)
        self.timer.timeout.connect(self.check_restart_required)

    def check_restart_required(self):
        restart_required = self.bitcoin.restart_required
        self.bitcoin_restart_required.setText(f'Bitcoin: {self.bitcoin.restart_required}')
        if restart_required:
            self.section_name.show()
            self.bitcoin_restart_required.show()
        else:
            self.section_name.hide()
            self.bitcoin_restart_required.hide()
