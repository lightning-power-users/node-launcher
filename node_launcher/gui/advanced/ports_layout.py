from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.horizontal_line import HorizontalLine
from node_launcher.gui.components.selectable_text import SelectableText
from node_launcher.node_set import NodeSet


class PortsLayout(QGridLayout):
    def __init__(self, node_set: NodeSet):
        super(PortsLayout, self).__init__()
        self.node_set = node_set

        self.network_ports = SelectableText(
            f'Network Ports'
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
            f'Client Ports'
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
