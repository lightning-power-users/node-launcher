from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QSystemTrayIcon, QWidget

from .assets.asset_access import asset_access
from .menu.menu import Menu
from node_launcher.node_set import NodeSet


class SystemTray(QSystemTrayIcon):
    def __init__(self, parent: QWidget, node_set: NodeSet):
        super(SystemTray, self).__init__(parent=parent)
        self.node_set = node_set
        self.set_red()
        self.menu = Menu(node_set=node_set, system_tray=self)
        self.setContextMenu(self.menu)

        self.node_set.bitcoind_node.process.notification.connect(
            self.show_message
        )

        self.node_set.lnd_node.process.notification.connect(
            self.show_message
        )

        self.node_set.lnd_node.process.set_icon_color.connect(
            self.set_icon
        )

    def set_icon(self, color: str):
        path = asset_access.get_asset_full_path(f'bitcoin_logo_{color}.png')
        pixmap = QPixmap(path)
        icon = QIcon(pixmap)
        self.setIcon(icon)

    def set_red(self):
        self.set_icon('red')

    def set_blue(self):
        self.set_icon('blue')

    def set_green(self):
        self.set_icon('green')

    def show_message(self,
                     title: str,
                     message: str = '',
                     icon=QSystemTrayIcon.Information,
                     timeout: int = 10):
        milliseconds_timeout_hint = timeout * 1000
        self.showMessage(title, message, icon, milliseconds_timeout_hint)
