from PySide2 import QtCore
from PySide2.QtCore import QCoreApplication, Slot
from PySide2.QtWidgets import QApplication, QWidget

from node_launcher.gui.system_tray import SystemTray
from node_launcher.node_set import NodeSet


class Application(QApplication):
    def __init__(self):
        super().__init__()

        self.node_set = NodeSet()
        self.parent = QWidget()
        self.parent.hide()
        self.parent.setWindowFlags(self.parent.windowFlags() & ~QtCore.Qt.Tool)

        self.system_tray = SystemTray(self.parent, self.node_set)

        self.setQuitOnLastWindowClosed(False)

        self.aboutToQuit.connect(self.quit_app)

        self.system_tray.show()

    @Slot()
    def quit_app(self):
        self.node_set.lnd.process.terminate()
        self.node_set.lnd.process.waitForFinished(2000)
        self.node_set.bitcoin.process.terminate()
        self.node_set.bitcoin.process.waitForFinished(2000)
        self.node_set.bitcoin.process.kill()

        QCoreApplication.exit(0)
