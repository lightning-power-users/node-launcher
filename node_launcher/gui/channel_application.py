from PySide2.QtCore import QCoreApplication, Slot
from PySide2.QtWidgets import QApplication

from node_launcher.gui.menu.nodes_manage.manage_dialogs.channels import \
    ChannelsDialog
from node_launcher.logging import log
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
