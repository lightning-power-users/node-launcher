from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QSystemTrayIcon, QWidget

from node_launcher.assets.asset_access import asset_access


class SystemTray(QSystemTrayIcon):
    def __init__(self, parent: QWidget):
        super(SystemTray, self).__init__(parent=parent)
        self.set_red()

    def set_icon(self, color: str):
        path = asset_access.get_asset_full_path(f'system_tray_icon_{color}.png')
        pixmap = QPixmap(path)
        icon = QIcon(pixmap)
        self.setIcon(icon)

    def set_red(self):
        self.set_icon('red')

    def set_orange(self):
        self.set_icon('orange')

    def set_green(self):
        self.set_icon('green')
