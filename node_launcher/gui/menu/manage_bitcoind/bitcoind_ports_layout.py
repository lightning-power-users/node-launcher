from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.horizontal_line import HorizontalLine
from node_launcher.gui.components.section_name import SectionName
from node_launcher.gui.components.selectable_text import SelectableText
from node_launcher.gui.components.warning_text import WarningText
from node_launcher.node_set.bitcoin import Bitcoin


class BitcoindPortsLayout(QGridLayout):
    def __init__(self, bitcoin: Bitcoin):
        super(BitcoindPortsLayout, self).__init__()
        self.bitcoin = bitcoin

        self.network_ports = SectionName(
            f'Network Ports (for <a '
            f'href="https://www.wikihow.com/Set-Up-Port-Forwarding-on-a-Router"'
            f'>port forwarding</a>)'
        )

        self.bitcoin_network_port = SelectableText(
            f'Bitcoin network peer port: {self.bitcoin.node_port}'
        )

        self.addWidget(self.network_ports)
        self.addWidget(self.bitcoin_network_port)

        self.addWidget(HorizontalLine())

        self.client_ports = SelectableText(
            f'Client Ports (you can lose money port forwarding these!)'
        )
        self.addWidget(self.client_ports)

        self.zmq_ports = SelectableText(
            f'Bitcoin ZMQ block/tx ports:'
            f' {self.bitcoin.zmq_block_port}'
            f'/{self.bitcoin.zmq_tx_port}'
        )
        self.addWidget(self.zmq_ports)

        self.rpc_port = SelectableText(
            f'Bitcoin RPC port: {self.bitcoin.rpc_port}'
        )
        self.addWidget(self.rpc_port)

        self.bitcoin_restart_required = WarningText(
            'Config file changed: Restart Bitcoin'
        )
        self.addWidget(self.bitcoin_restart_required)
        self.bitcoin_restart_required.hide()

        self.bitcoin.file.file_watcher.fileChanged.connect(self.refresh_bitcoin_ports)

    def refresh_bitcoin_ports(self):
        self.bitcoin_network_port.setText(
            f'Bitcoin network peer port: {self.bitcoin.node_port}'
        )
        self.zmq_ports.setText(
            f'Bitcoin ZMQ block/tx ports:'
            f' {self.bitcoin.zmq_block_port}'
            f'/{self.bitcoin.zmq_tx_port}'
        )
        self.rpc_port.setText(
            f'Bitcoin RPC port: {self.bitcoin.rpc_port}'
        )
        self.check_restart_required()

    def check_restart_required(self):
        if self.bitcoin.restart_required:
            self.bitcoin_restart_required.show()
        else:
            self.bitcoin_restart_required.hide()

