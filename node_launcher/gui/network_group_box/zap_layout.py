from PySide2 import QtWidgets

from node_launcher.gui.components.layouts import QGridLayout
from node_launcher.gui.horizontal_line import HorizontalLine
from node_launcher.gui.network_group_box.section_name import SectionName
from node_launcher.gui.utilities import copy_to_clipboard
from node_launcher.node_set import NodeSet


class ZapLayout(QGridLayout):
    node_set: NodeSet

    def __init__(self, node_set: NodeSet):
        super(ZapLayout, self).__init__()
        self.node_set = node_set
        columns = 2

        self.addWidget(SectionName('Zap'), column_span=columns)

        zap_buttons_layout = QtWidgets.QHBoxLayout()
        # Copy Host gRPC API URL button
        self.copy_grpc_url_button = QtWidgets.QPushButton('Host (gRPC)')
        # noinspection PyUnresolvedReferences
        self.copy_grpc_url_button.clicked.connect(
            lambda: copy_to_clipboard(self.node_set.lnd.grpc_url)
        )
        zap_buttons_layout.addWidget(self.copy_grpc_url_button)

        # Copy TLS Cert command button
        self.copy_tls_cert_path_button = QtWidgets.QPushButton('TLS Cert Path')
        # noinspection PyUnresolvedReferences
        self.copy_tls_cert_path_button.clicked.connect(
            lambda: copy_to_clipboard(self.node_set.lnd.tls_cert_path)
        )
        zap_buttons_layout.addWidget(self.copy_tls_cert_path_button, same_row=True, column=2)

        # Copy Admin Macaroon Path command button
        self.copy_admin_macaroon_path_button = QtWidgets.QPushButton('Macaroon Path')
        # noinspection PyUnresolvedReferences
        self.copy_admin_macaroon_path_button.clicked.connect(
            lambda: copy_to_clipboard(self.node_set.lnd.admin_macaroon_path)
        )
        zap_buttons_layout.addWidget(self.copy_admin_macaroon_path_button, same_row=True, column=3)

        self.addLayout(zap_buttons_layout, column_span=columns)
        self.addWidget(HorizontalLine(), column_span=columns)
