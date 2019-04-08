import webbrowser

from PySide2.QtCore import QCoreApplication
from PySide2.QtGui import QClipboard, QPixmap
from PySide2.QtWidgets import QMenu, QLabel

from node_launcher.gui.menu.manage_bitcoind.bitcoind_manager_tabs_dialog import \
    BitcoindManagerTabsDialog
from node_launcher.gui.utilities import reveal
from node_launcher.node_set import NodeSet
from node_launcher.services.lndconnect import get_deprecated_lndconnect_url, \
    get_qrcode_img


class Menu(QMenu):
    def __init__(self, node_set: NodeSet, system_tray):
        super().__init__()
        self.node_set = node_set
        self.system_tray = system_tray

        # Bitcoind
        self.bitcoind_status_action = self.addAction('bitcoind off')
        self.bitcoind_status_action.setEnabled(False)

        self.bitcoin_manager = BitcoindManagerTabsDialog(
            bitcoin=self.node_set.bitcoin,
            system_tray=self.system_tray
        )
        self.bitcoin_manage_action = self.addAction('Manage Bitcoind')
        self.bitcoin_manage_action.triggered.connect(
            self.bitcoin_cli_widget.show
        )

        self.addSeparator()

        # LND

        self.lnd_status_action = self.addAction('lnd off')
        self.lnd_status_action.setEnabled(False)

        self.lnd_manager = LndManagerTabsDialog()
        self.lnd_manage_action = self.addAction('Manage LND')
        self.lnd_manage_action.triggered.connect(
            self.lnd_manager.show
        )

        self.addSeparator()

        # Joule

        self.joule_status_action = self.addAction('Joule Browser UI')
        self.joule_status_action.setEnabled(False)
        self.joule_url_action = self.addAction('Copy Node URL (REST)')
        self.joule_macaroons_action = self.addAction('Show Macaroons')

        self.joule_url_action.triggered.connect(
            lambda: QClipboard().setText(self.node_set.lnd.rest_url)
        )

        self.joule_macaroons_action.triggered.connect(
            lambda: reveal(self.node_set.lnd.macaroon_path)
        )

        self.addSeparator()

        # Zap

        self.zap_status_action = self.addAction('Zap Desktop UI')
        self.zap_status_action.setEnabled(False)

        # This should soon be replaced with using the get_lndconnect_url method
        old_lndconnect_url = get_deprecated_lndconnect_url(
            self.node_set.lnd.grpc_url.split(':')[0],
            self.node_set.lnd.grpc_url.split(':')[1],
            self.node_set.lnd.tls_cert_path,
            self.node_set.lnd.admin_macaroon_path
        )
        self.zap_open_action = self.addAction('Open Zap Desktop')
        self.zap_open_action.triggered.connect(
            lambda: webbrowser.open(old_lndconnect_url)
        )

        qrcode_img = get_qrcode_img(
            self.node_set.lnd.file['externalip'],
            self.node_set.lnd.grpc_url.split(':')[1],
            self.node_set.lnd.tls_cert_path,
            self.node_set.lnd.admin_macaroon_path
        )
        qrcode_img.save('qrcode.png', 'PNG')

        pixmap = QPixmap('qrcode.png')
        pixmap = pixmap.scaledToWidth(400)
        qrcode_label = QLabel()
        qrcode_label.setWindowTitle('Zap QR Code')
        qrcode_label.resize(400, 400)
        qrcode_label.setPixmap(pixmap)
        self.show_zap_qrcode_action = self.addAction('Pair Zap Mobile')
        self.show_zap_qrcode_button.clicked.connect(
            qrcode_label.show
        )

        self.addSeparator()

        # Quit
        self.quit_action = self.addAction('Quit')

        self.quit_action.triggered.connect(
            lambda _: QCoreApplication.exit(0)
        )
