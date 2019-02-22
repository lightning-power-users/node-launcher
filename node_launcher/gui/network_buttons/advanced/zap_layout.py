import webbrowser

from PySide2 import QtWidgets
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QLabel

from node_launcher.services.lndconnect import get_deprecated_lndconnect_url, \
    get_qrcode_img

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.horizontal_line import HorizontalLine
from node_launcher.gui.components.section_name import SectionName
from node_launcher.node_set import NodeSet


class ZapLayout(QGridLayout):
    node_set: NodeSet

    def __init__(self, node_set: NodeSet):
        super(ZapLayout, self).__init__()
        self.qrcode_label = None
        self.node_set = node_set
        columns = 2

        self.section_name = SectionName('''
<a href="https://medium.com/lightning-power-users/easy-lightning-with-node-launcher-zap-488133edfbd">
    Zap Desktop Wallet
</a>
''')

        self.open_zap_desktop_button = QtWidgets.QPushButton('Open Zap Desktop')
        self.open_zap_desktop_button.clicked.connect(self.open_zap_desktop)

        # self.show_zap_qrcode_button = QtWidgets.QPushButton('Show QR Code')
        # self.show_zap_qrcode_button.clicked.connect(self.show_zap_qrcode)

        self.addWidget(self.section_name, column_span=columns)
        self.addWidget(self.open_zap_desktop_button, column_span=columns)
        # self.addWidget(self.show_zap_qrcode_button, same_row=True, column=2)
        self.addWidget(HorizontalLine(), column_span=columns)

    def set_button_state(self):
        self.open_zap_desktop_button.setEnabled(self.node_set.lnd.is_unlocked)
        # self.show_zap_qrcode_button.setEnabled(self.node_set.lnd.is_unlocked)

    def open_zap_desktop(self):
        # This should soon be replaced with using the get_lndconnect_url method
        old_lndconnect_url = get_deprecated_lndconnect_url(
            self.node_set.lnd.grpc_url.split(':')[0],
            self.node_set.lnd.grpc_url.split(':')[1],
            self.node_set.lnd.tls_cert_path,
            self.node_set.lnd.admin_macaroon_path
        )
        webbrowser.open(old_lndconnect_url)

    def show_zap_qrcode(self):
        qrcode_img = get_qrcode_img(
            self.node_set.lnd.tlsextraip,
            self.node_set.lnd.grpc_url.split(':')[1],
            self.node_set.lnd.tls_cert_path,
            self.node_set.lnd.admin_macaroon_path
        )
        qrcode_img.save('qrcode.png', 'PNG')

        pixmap = QPixmap('qrcode.png')
        pixmap = pixmap.scaledToWidth(400)
        self.qrcode_label = QLabel()
        self.qrcode_label.setWindowTitle('Zap QR Code')
        self.qrcode_label.resize(400, 400)
        self.qrcode_label.setPixmap(pixmap)
        self.qrcode_label.show()
