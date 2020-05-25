from PySide2 import QtCore
from PySide2.QtCore import QCoreApplication, Slot, Qt, QThreadPool
from PySide2.QtWidgets import QApplication, QWidget, QMessageBox

from node_launcher.constants import NODE_LAUNCHER_RELEASE, UPGRADE
from node_launcher.gui.components.thread_worker import Worker
from node_launcher.gui.menu.nodes_manage.manage_dialogs.channels import \
    ChannelsDialog
from node_launcher.gui.system_tray import SystemTray
from node_launcher.logging import log
from node_launcher.node_set import NodeSet
from node_launcher.launcher_software import LauncherSoftware
from node_launcher.node_set.lnd.lnd_client import LndClient


class ChannelApplication(QApplication):
    def __init__(self, lnd_client: LndClient):
        super().__init__()
        self.aboutToQuit.connect(self.quit_app)
        self.channels_dialog = ChannelsDialog(lnd_client=lnd_client)

    def start(self):
        self.channels_dialog.show()
        status = self.exec_()
        return status

    @Slot()
    def quit_app(self):
        log.debug('quit_app')
        QCoreApplication.exit(0)
