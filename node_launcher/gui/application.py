from PySide2 import QtCore
from PySide2.QtCore import QCoreApplication, Slot, Qt, QThreadPool
from PySide2.QtWidgets import QApplication, QWidget, QMessageBox

from node_launcher.constants import NODE_LAUNCHER_RELEASE, UPGRADE
from node_launcher.gui.components.thread_worker import Worker
from node_launcher.gui.system_tray import SystemTray
from node_launcher.logging import log
from node_launcher.node_set import NodeSet
from node_launcher.launcher_software import LauncherSoftware


class Application(QApplication):
    def __init__(self):
        super().__init__()

        self.parent = QWidget()
        self.parent.hide()
        self.parent.setWindowFlags(self.parent.windowFlags() & ~QtCore.Qt.Tool)
        self.setQuitOnLastWindowClosed(False)
        self.aboutToQuit.connect(self.quit_app)

        self.node_set = NodeSet()
        self.system_tray = SystemTray(self.parent, self.node_set)

    def start(self):
        threadpool = QThreadPool()
        worker = Worker(fn=self.check_version)
        threadpool.start(worker)

        self.system_tray.show()
        self.node_set.start()
        status = self.exec_()
        return status

    @staticmethod
    def check_version():
        latest_version = LauncherSoftware().get_latest_release_version()
        if latest_version is None:
            return
        latest_major, latest_minor, latest_bugfix = latest_version.split('.')
        major, minor, bugfix = NODE_LAUNCHER_RELEASE.split('.')

        major_upgrade = latest_major > major

        minor_upgrade = (latest_major == major
                         and latest_minor > minor)

        bugfix_upgrade = (latest_major == major
                          and latest_minor == minor
                          and latest_bugfix > bugfix)

        if major_upgrade or minor_upgrade or bugfix_upgrade:
            message_box = QMessageBox()
            message_box.setTextFormat(Qt.RichText)
            message_box.setText(UPGRADE)
            message_box.setInformativeText(
                f'Your version: {NODE_LAUNCHER_RELEASE}\n'
                f'New version: {latest_version}'
            )
            message_box.exec_()

    @Slot()
    def quit_app(self):
        log.debug('quit_app')
        self.system_tray.show_message(title='Stopping LND...')
        self.node_set.lnd_node.stop()
        self.node_set.lnd_node.process.waitForFinished(-1)

        self.node_set.bitcoind_node.stop()
        self.system_tray.show_message(title='Stopping bitcoind...')
        self.node_set.bitcoind_node.process.waitForFinished(-1)

        self.node_set.tor_node.process.kill()
        self.node_set.tor_node.process.waitForFinished(-1)

        self.system_tray.show_message(title='Exiting Node Launcher', timeout=1)

        QCoreApplication.exit(0)
