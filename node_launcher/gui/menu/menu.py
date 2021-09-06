import webbrowser

from node_launcher.gui.qt import QCoreApplication, QClipboard, QMenu, QAction

from node_launcher.gui.menu.menu_actions.nodes_menu.bitcoind_status_action import \
    BitcoindStatusAction
from node_launcher.gui.menu.menu_actions.nodes_menu.lnd_status_action import \
    LndStatusAction
from node_launcher.gui.menu.menu_actions.nodes_menu.node_manage_action import \
    NodeManageAction
from node_launcher.gui.menu.menu_actions.separator_action import SeparatorAction
from node_launcher.gui.menu.menu_actions.nodes_menu.tor_status_action import \
    TorStatusAction
from node_launcher.gui.utilities import reveal
from node_launcher.node_set import NodeSet


class Menu(QMenu):
    def __init__(self, node_set: NodeSet, system_tray, parent):
        super().__init__()
        self.node_set = node_set
        self.system_tray = system_tray
        self.cache = []

        default_actions = [
            TorStatusAction(self.node_set.tor_node, parent=parent),
            BitcoindStatusAction(self.node_set.bitcoind_node, parent=parent),
            LndStatusAction(self.node_set.lnd_node, parent=parent),
            NodeManageAction(node_set=node_set, system_tray=system_tray),
            SeparatorAction()
        ]

        for action in default_actions:
            self.add_action(action)

        self.joule_url_action = self.addAction('Copy Node URL (REST)')

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

    def add_action(self, action: QAction):
        self.cache.append(action)
        self.addAction(action)

    def copy_rest_url(self):
        QClipboard().setText(self.node_set.lnd_node.configuration.rest_url)

    def reveal_macaroon_path(self):
        reveal(self.node_set.lnd_node.configuration.macaroon_path)
