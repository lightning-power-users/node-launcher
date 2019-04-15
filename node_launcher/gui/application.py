from PySide2 import QtCore
from PySide2.QtCore import QCoreApplication, Slot, QTimer, Qt, QThreadPool, QProcess
from PySide2.QtWidgets import QApplication, QWidget, QMessageBox

from node_launcher.constants import NODE_LAUNCHER_RELEASE, UPGRADE
from node_launcher.gui.components.thread_worker import Worker
from node_launcher.gui.system_tray import SystemTray
from node_launcher.node_set import NodeSet
from node_launcher.node_set.bitcoind_client import Proxy
from node_launcher.services.launcher_software import LauncherSoftware


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

        self.system_tray.show_message(
            title='Nodes starting...',
            message='Bitcoin and Lightning are syncing'
        )

        self.node_set.bitcoin.file.file_watcher.fileChanged.connect(self.check_restart_required)
        self.node_set.lnd.file.file_watcher.fileChanged.connect(self.check_restart_required)

        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.check_restart_required)

        self.threadpool = QThreadPool()
        worker = Worker(fn=self.check_version)
        self.threadpool.start(worker)

    def check_restart_required(self):
        if self.node_set.bitcoin.restart_required or self.node_set.lnd.restart_required:
            pass
        else:
            pass

    @staticmethod
    def check_version(progress_callback):
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
        self.system_tray.show_message(title='Stopping LND and bitcoind...')

        if self.node_set.lnd.process.state() == QProcess.Running:
            self.node_set.lnd.client.stop()
        if self.node_set.bitcoin.process.state() == QProcess.Running:
            Proxy(btc_conf_file=self.node_set.bitcoin.file.path,
                  service_port=self.node_set.bitcoin.rpc_port).call('stop')

        self.node_set.tor.process.kill()

        self.node_set.lnd.process.waitForFinished(-1)
        self.node_set.bitcoin.process.waitForFinished(-1)
        self.node_set.tor.process.waitForFinished(-1)

        self.system_tray.show_message(title='Exiting Node Launcher', timeout=1)

        QCoreApplication.exit(0)
