import webbrowser

from PySide2.QtCore import QCoreApplication
from PySide2.QtGui import QClipboard
from PySide2.QtWidgets import QMenu

from node_launcher.gui.menu.manage_lnd.lnd_manager_tabs_dialog import \
    LndManagerTabsDialog
from node_launcher.gui.menu.manage_lnd.zap_qrcode_label import ZapQrcodeLabel
from .manage_bitcoind import BitcoindManagerTabsDialog
from node_launcher.gui.utilities import reveal
from node_launcher.node_set import NodeSet


class Menu(QMenu):
    def __init__(self, node_set: NodeSet, system_tray):
        super().__init__()
        self.node_set = node_set
        self.system_tray = system_tray

        # Bitcoind
        self.bitcoind_status_action = self.addAction('bitcoind off')
        self.bitcoind_status_action.setEnabled(False)

        self.bitcoind_manager_tabs_dialog = BitcoindManagerTabsDialog(
            bitcoin=self.node_set.bitcoin,
            system_tray=self.system_tray
        )
        self.bitcoin_manage_action = self.addAction('Manage Bitcoind')
        self.bitcoin_manage_action.triggered.connect(
            self.bitcoind_manager_tabs_dialog.show
        )

        self.addSeparator()

        # LND
        self.lnd_status_action = self.addAction('lnd off')
        self.lnd_status_action.setEnabled(False)

        self.lnd_manager_tabs_dialog = LndManagerTabsDialog(
            lnd=self.node_set.lnd,
            system_tray=self.system_tray
        )
        self.lnd_manage_action = self.addAction('Manage LND')
        self.lnd_manage_action.triggered.connect(
            self.lnd_manager_tabs_dialog.show
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
        self.zap_open_action = self.addAction('Open Zap Desktop')
        self.zap_open_action.triggered.connect(
            lambda: webbrowser.open(self.node_set.lnd.lndconnect_url)
        )
        self.show_zap_qrcode_action = self.addAction('Pair Zap Mobile')
        self.show_zap_qrcode_button.clicked.connect(
            ZapQrcodeLabel(self.node_set.lnd.lndconnect_qrcode).show
        )

        self.addSeparator()

        # Quit
        self.quit_action = self.addAction('Quit')
        self.quit_action.triggered.connect(
            lambda _: QCoreApplication.exit(0)
        )
