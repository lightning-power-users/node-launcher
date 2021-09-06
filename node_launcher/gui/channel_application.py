import sys

from node_launcher.gui.menu.nodes_manage.manage_dialogs.channels import \
    ChannelsDialog
from node_launcher.gui.qt import QCoreApplication, Slot, QApplication
from node_launcher.logging import log
from node_launcher.node_set.lnd.lnd_client import LndClient
from node_launcher.node_set.lnd.lnd_node import LndNode


class ChannelApplication(QApplication):
    def __init__(self, node: LndNode = None, client: LndClient = None):
        super().__init__(sys.argv)
        self.aboutToQuit.connect(self.quit_app)
        if node is not None:
            client = node.client
        self.channels_dialog = ChannelsDialog(client=client)

    def start(self):
        self.channels_dialog.show()
        status = self.exec_()
        return status

    @Slot()
    def quit_app(self):
        log.debug('quit_app')
        QCoreApplication.exit(0)
