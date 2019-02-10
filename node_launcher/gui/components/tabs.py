from PySide2.QtWidgets import QTabWidget, QWidget

from node_launcher.gui.cli.cli import CliWidget
from node_launcher.gui.network_buttons.network_widget import NetworkWidget


class Tabs(QTabWidget):
    def __init__(self, parent: QWidget, network_widget: NetworkWidget):
        super(Tabs, self).__init__(parent)
        self.setTabPosition(QTabWidget.North)
        self.addTab(network_widget, 'Network')
        lncli_widget = CliWidget(network_widget.node_set.lnd.software.lncli,
                                 network_widget.node_set.lnd.lncli_arguments())
        self.addTab(lncli_widget, 'lncli')

        bitcoin_cli_widget = CliWidget(network_widget.node_set.bitcoin.software.bitcoin_cli,
                                 network_widget.node_set.bitcoin.bitcoin_cli_arguments())
        self.addTab(bitcoin_cli_widget, 'bitcoin-cli')
