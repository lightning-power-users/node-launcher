from node_launcher.gui.components.copy_button import CopyButton
from node_launcher.gui.components.layouts import QGridLayout
from node_launcher.gui.horizontal_line import HorizontalLine
from node_launcher.gui.network_buttons.section_name import SectionName
from node_launcher.node_set import NodeSet


class ZapLayout(QGridLayout):
    node_set: NodeSet

    def __init__(self, node_set: NodeSet):
        super(ZapLayout, self).__init__()
        self.node_set = node_set
        columns = 3

        self.addWidget(SectionName('<a href="https://github.com/LN-Zap/zap-desktop/blob/master/README.md">Zap Desktop Wallet</a>'), column_span=columns)

        self.copy_grpc_url = CopyButton('Host gRPC', self.node_set.lnd.grpc_url)
        self.addLayout(self.copy_grpc_url)

        self.copy_tls_cert_path = CopyButton('TLS Cert Path',
                                             self.node_set.lnd.tls_cert_path)
        self.addLayout(self.copy_tls_cert_path, same_row=True, column=2)

        self.copy_admin_macaroon_path = CopyButton(
            'Macaroon Path',
            self.node_set.lnd.admin_macaroon_path
        )
        self.addLayout(self.copy_admin_macaroon_path, same_row=True, column=3)

        self.addWidget(HorizontalLine(), column_span=columns)
