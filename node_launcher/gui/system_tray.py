from node_launcher.gui.qt import QIcon, QPixmap, QImage, QSystemTrayIcon, QWidget
from node_launcher.gui.assets.asset_access import asset_access
from node_launcher.gui.menu.menu import Menu
from node_launcher.node_set import NodeSet
from node_launcher.app_logging import log


class SystemTray(QSystemTrayIcon):
    def __init__(self, parent: QWidget, node_set: NodeSet):
        super(SystemTray, self).__init__(parent=parent)
        self.node_set = node_set
        self.set_zero()
        self.menu = Menu(node_set=node_set, system_tray=self, parent=parent)
        self.setContextMenu(self.menu)

        if self.node_set.bitcoind_node:
            self.node_set.bitcoind_node.process.notification.connect(
                self.show_message
            )

        self.node_set.lnd_node.process.notification.connect(
            self.show_message
        )

        self.node_set.set_icon_number.connect(
            self.set_icon
        )

    @staticmethod
    def get_path(number: int):
        base_path = 'Bitcoin-Icons/png/filled/node'
        if number == 1:
            word = 'connection'
        elif number == 4:
            return base_path + '.png'
        else:
            word = 'connections'
        return base_path + f'-{number} {word}.png'

    def set_icon(self, number: int):
        path = asset_access.get_asset_full_path(self.get_path(number))
        image = QImage(path)
        image.invertPixels()
        icon = QIcon(QPixmap.fromImage(image))
        self.setIcon(icon)

    def set_zero(self):
        self.set_icon(0)

    def set_one(self):
        self.set_icon(1)

    def set_two(self):
        self.set_icon(2)

    def set_three(self):
        self.set_icon(3)

    def set_four(self):
        self.set_icon(4)

    def show_message(self,
                     title: str,
                     message: str = '',
                     icon=QSystemTrayIcon.Information,
                     timeout: int = 10):
        milliseconds_timeout_hint = timeout * 1000
        log.debug('show_message', title=title, message=message, timeout=timeout)
        self.showMessage(title, message, icon, milliseconds_timeout_hint)
