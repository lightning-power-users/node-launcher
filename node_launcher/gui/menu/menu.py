from node_launcher.gui.qt import QCoreApplication, QGuiApplication, QMenu, QAction
from node_launcher.gui.menu.menu_actions.nodes_menu.bitcoind_status_action import \
    BitcoindStatusAction
from node_launcher.gui.menu.menu_actions.nodes_menu.lnd_status_action import \
    LndStatusAction
from node_launcher.gui.menu.menu_actions.separator_action import SeparatorAction
from node_launcher.gui.menu.menu_actions.nodes_menu.tor_status_action import \
    TorStatusAction
from node_launcher.gui.reveal_directory import reveal_directory
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
            SeparatorAction()
        ]

        for action in default_actions:
            self.add_action(action)

        # Joule
        self.joule_status_action = self.addAction('Joule Browser UI')
        self.joule_status_action.setEnabled(False)
        self.joule_url_action = self.addAction('Copy Node URL (REST)')
        self.joule_macaroons_action = self.addAction('Show Macaroons')
        self.joule_url_action.triggered.connect(self.copy_rest_url)
        self.joule_macaroons_action.triggered.connect(self.reveal_macaroon_path)

        self.addSeparator()
        # Todo: add debug

        # Quit
        self.quit_action = self.addAction('Quit')
        self.quit_action.triggered.connect(
            lambda _: QCoreApplication.exit(0)
        )

    def add_action(self, action: QAction):
        self.cache.append(action)
        self.addAction(action)

    def copy_rest_url(self):
        QGuiApplication.clipboard().setText(self.node_set.lnd_node.configuration.rest_url)

    def reveal_macaroon_path(self):
        reveal_directory(self.node_set.lnd_node.configuration.macaroon_path)
