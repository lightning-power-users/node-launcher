from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.horizontal_line import HorizontalLine
from node_launcher.gui.components.section_name import SectionName
from node_launcher.gui.components.selectable_text import SelectableText
from node_launcher.gui.components.warning_text import WarningText
from node_launcher.node_set import NodeSet


class PortsLayout(QGridLayout):
    def __init__(self, node_set: NodeSet):
        super(PortsLayout, self).__init__()
        self.node_set = node_set

        self.network_ports = SectionName(
            f'Network Ports (for <a '
            f'href="https://www.wikihow.com/Set-Up-Port-Forwarding-on-a-Router"'
            f'>port forwarding</a>)'
        )

        self.bitcoin_network_port = SelectableText(
            f'Bitcoin network peer port: {self.node_set.bitcoin.node_port}'
        )

        self.lnd_network_port = SelectableText(
            f'LND network peer port: {self.node_set.lnd.node_port}'
        )

        self.addWidget(self.network_ports)
        self.addWidget(self.bitcoin_network_port)
        self.addWidget(self.lnd_network_port)

        self.addWidget(HorizontalLine())

        self.client_ports = SelectableText(
            f'Client Ports (you can lose money port forwarding these!)'
        )
        self.addWidget(self.client_ports)

        self.zmq_ports = SelectableText(
            f'Bitcoin ZMQ block/tx ports:'
            f' {self.node_set.bitcoin.zmq_block_port}'
            f'/{self.node_set.bitcoin.zmq_tx_port}'
        )
        self.addWidget(self.zmq_ports)

        self.rpc_port = SelectableText(
            f'Bitcoin RPC port: {self.node_set.bitcoin.rpc_port}'
        )
        self.addWidget(self.rpc_port)

        self.grpc_port = SelectableText(
            f'LND gRPC port: {self.node_set.lnd.grpc_port}'
        )
        self.addWidget(self.grpc_port)

        self.rest_port = SelectableText(
            f'LND REST port: {self.node_set.lnd.rest_port}'
        )
        self.addWidget(self.rest_port)
        self.bitcoin_restart_required = WarningText(
            'Config file changed: Restart Bitcoin'
        )
        self.addWidget(self.bitcoin_restart_required)
        self.bitcoin_restart_required.hide()
        self.lnd_restart_required = WarningText(
            'Config file changed: Restart LND'
        )
        self.addWidget(self.lnd_restart_required)
        self.lnd_restart_required.hide()

        self.node_set.bitcoin.file.file_watcher.fileChanged.connect(self.refresh_bitcoin_ports)
        self.node_set.lnd.file.file_watcher.fileChanged.connect(self.refresh_lnd_ports)


    def refresh_bitcoin_ports(self):
        self.bitcoin_network_port.setText(
            f'Bitcoin network peer port: {self.node_set.bitcoin.node_port}'
        )
        self.zmq_ports.setText(
            f'Bitcoin ZMQ block/tx ports:'
            f' {self.node_set.bitcoin.zmq_block_port}'
            f'/{self.node_set.bitcoin.zmq_tx_port}'
        )
        self.rpc_port.setText(
            f'Bitcoin RPC port: {self.node_set.bitcoin.rpc_port}'
        )
        self.check_restart_required()

    def refresh_lnd_ports(self):
        self.lnd_network_port.setText(
            f'LND network peer port: {self.node_set.lnd.node_port}'
        )
        self.grpc_port.setText(
            f'LND gRPC port: {self.node_set.lnd.grpc_port}'
        )
        self.rest_port.setText(
            f'LND REST port: {self.node_set.lnd.rest_port}'
        )
        self.check_restart_required()

    def check_restart_required(self):
        if self.node_set.bitcoin.restart_required:
            self.bitcoin_restart_required.show()
        else:
            self.bitcoin_restart_required.hide()

        if self.node_set.lnd.restart_required:
            self.lnd_restart_required.show()
        else:
            self.lnd_restart_required.hide()
