import webbrowser

from PySide2.QtCore import QCoreApplication
from PySide2.QtGui import QClipboard
from PySide2.QtWidgets import QMenu

from .node_manager.node_manager_tabs_dialog import NodeManagerTabsDialog
from node_launcher.gui.utilities import reveal
from node_launcher.node_set import NodeSet


class Menu(QMenu):
    def __init__(self, node_set: NodeSet, system_tray):
        super().__init__()
        self.node_set = node_set
        self.system_tray = system_tray

        # Tor
        self.tor_status_action = self.addAction('Tor: off')
        self.tor_status_action.setEnabled(False)
        self.node_set.tor_node.status.connect(
            lambda line: self.tor_status_action.setText('Tor: ' + line.replace('_', ' '))
        )

        # Bitcoind
        self.bitcoind_status_action = self.addAction('Bitcoind: off')
        self.bitcoind_status_action.setEnabled(False)
        self.node_set.bitcoind_node.status.connect(
            lambda line: self.bitcoind_status_action.setText('Bitcoind: ' + line.replace('_', ' '))
        )

        # LND
        self.lnd_status_action = self.addAction('LND: off')
        self.lnd_status_action.setEnabled(False)
        self.node_set.lnd_node.status.connect(
            lambda line: self.lnd_status_action.setText('LND: ' + line.replace('_', ' '))
        )

        self.bitcoind_manager_tabs_dialog = NodeManagerTabsDialog(
            node_set=self.node_set,
            system_tray=self.system_tray
        )
        self.bitcoin_manage_action = self.addAction('Manage Nodes')
        self.bitcoin_manage_action.triggered.connect(
            self.bitcoind_manager_tabs_dialog.show
        )
        self.addSeparator()

        # Joule
        self.joule_status_action = self.addAction('Joule Browser UI')
        self.joule_status_action.setEnabled(False)
        self.joule_url_action = self.addAction('Copy Node URL (REST)')
        self.joule_macaroons_action = self.addAction('Show Macaroons')
        self.joule_url_action.triggered.connect(self.copy_rest_url)
        self.joule_macaroons_action.triggered.connect(self.reveal_macaroon_path)

        self.addSeparator()

        # Zap
        self.zap_status_action = self.addAction('Zap Desktop UI')
        self.zap_status_action.setEnabled(False)
        self.zap_open_action = self.addAction('Open Zap Desktop')
        self.zap_open_action.triggered.connect(
            lambda: webbrowser.open(self.node_set.lnd_node.configuration.lndconnect_url)
        )
        # Todo: reenable when Zap mobile supports Tor
        # self.zap_qr_code_label = ZapQrcodeLabel(
        #     configuration=self.node_set.lnd_node.configuration
        # )
        # self.show_zap_qrcode_action = self.addAction('Pair Zap Mobile')
        # self.show_zap_qrcode_action.triggered.connect(
        #     self.zap_qr_code_label.show
        # )

        self.addSeparator()

        # Quit
        self.quit_action = self.addAction('Quit')
        self.quit_action.triggered.connect(
            lambda _: QCoreApplication.exit(0)
        )

    def copy_rest_url(self):
        QClipboard().setText(self.node_set.lnd_node.configuration.rest_url)

    def reveal_macaroon_path(self):
        reveal(self.node_set.lnd_node.configuration.macaroon_path)
