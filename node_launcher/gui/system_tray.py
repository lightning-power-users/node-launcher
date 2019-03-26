from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QSystemTrayIcon, QWidget


class SystemTray(QSystemTrayIcon):
    def __init__(self, icon: QIcon, parent: QWidget):
        super(SystemTray, self).__init__(icon, parent)
