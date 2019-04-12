from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.horizontal_line import HorizontalLine
from node_launcher.gui.components.section_name import SectionName
from node_launcher.gui.components.selectable_text import SelectableText
from node_launcher.gui.components.warning_text import WarningText
from node_launcher.node_set.lnd import Lnd


class LndPortsLayout(QGridLayout):
    def __init__(self, lnd: Lnd):
        super(LndPortsLayout, self).__init__()
        self.lnd = lnd

        self.network_ports = SectionName(
            f'Network Ports (for <a '
            f'href="https://www.wikihow.com/Set-Up-Port-Forwarding-on-a-Router"'
            f'>port forwarding</a>)'
        )
        self.addWidget(self.network_ports)

        self.lnd_network_port = SelectableText(
            f'LND network peer port: {self.lnd.node_port}'
        )
        self.addWidget(self.lnd_network_port)

        self.addWidget(HorizontalLine())

        self.client_ports = SelectableText(
            f'Client Ports (you can lose money port forwarding these!)'
        )
        self.addWidget(self.client_ports)

        self.grpc_port = SelectableText(
            f'LND gRPC port: {self.lnd.grpc_port}'
        )
        self.addWidget(self.grpc_port)

        self.rest_port = SelectableText(
            f'LND REST port: {self.lnd.rest_port}'
        )
        self.addWidget(self.rest_port)

        self.lnd_restart_required = WarningText(
            'Config file changed: Restart LND'
        )
        self.addWidget(self.lnd_restart_required)
        self.lnd_restart_required.hide()

        self.lnd.file.file_watcher.fileChanged.connect(self.refresh_lnd_ports)

    def refresh_lnd_ports(self):
        self.lnd_network_port.setText(
            f'LND network peer port: {self.lnd.node_port}'
        )
        self.grpc_port.setText(
            f'LND gRPC port: {self.lnd.grpc_port}'
        )
        self.rest_port.setText(
            f'LND REST port: {self.lnd.rest_port}'
        )
        self.check_restart_required()

    def check_restart_required(self):
        if self.lnd.restart_required:
            self.lnd_restart_required.show()
        else:
            self.lnd_restart_required.hide()
