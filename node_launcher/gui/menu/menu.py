from node_launcher.gui.menu.menu_actions.menu_action import MenuAction
from node_launcher.gui.qt import QCoreApplication, QGuiApplication, QMenu
from node_launcher.gui.reveal_directory import reveal_directory
from node_launcher.node_set import NodeSet


class Menu(QMenu):
    def __init__(self, node_set: NodeSet, system_tray, parent):
        super().__init__()
        self.node_set = node_set
        self.system_tray = system_tray

        self.node_set_status_action = MenuAction('Connecting...')
        self.node_set_status_action.setText('Connecting...')
        self.node_set_status_action.setEnabled(False)
        self.setVisible(True)
        self.addAction(self.node_set_status_action)

        self.addSeparator()
        # Todo: add debug

        # Quit
        self.quit_action = self.addAction('Quit')
        self.quit_action.triggered.connect(
            lambda _: QCoreApplication.exit(0)
        )

    def copy_rest_url(self):
        QGuiApplication.clipboard().setText(self.node_set.lnd_node.configuration.rest_url)

    def reveal_macaroon_path(self):
        reveal_directory(self.node_set.lnd_node.configuration.macaroon_path)
