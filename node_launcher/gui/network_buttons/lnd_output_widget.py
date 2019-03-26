import os

from PySide2.QtCore import QByteArray, QThreadPool, QProcess, Qt
from PySide2.QtWidgets import QDialog, QTextEdit
from grpc._channel import _Rendezvous

from node_launcher.constants import keyring
from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.thread_worker import Worker
from node_launcher.gui.system_tray import SystemTray
from node_launcher.logging import log
from node_launcher.node_set import NodeSet
from node_launcher.node_set.lnd_client import LndClient


class LndOutputWidget(QDialog):
    node_set: NodeSet
    process: QProcess
    system_tray: SystemTray

    def __init__(self, node_set: NodeSet, system_tray: SystemTray):
        super().__init__()
        self.node_set = node_set
        self.system_tray = system_tray
        self.process = node_set.lnd.process
        self.setWindowTitle('LND Output')
        self.layout = QGridLayout()

        self.threadpool = QThreadPool()

        self.output = QTextEdit()
        self.output.acceptRichText = True

        self.layout.addWidget(self.output)
        self.setLayout(self.layout)

    def handle_error(self):
        output: QByteArray = self.process.readAllStandardError()
        message = output.data().decode('utf-8').strip()
        self.output.append(message)

    @staticmethod
    def unlock_wallet(lnd, progress_callback, password: str):
        client = LndClient(lnd)
        try:
            client.unlock(password)
        except _Rendezvous as e:
            details = e.details()
            log.warning(
                'unlock_wallet failed',
                details=details,
                exc_info=True
            )
            return details

    def handle_unlock_wallet(self, details: str):
        if details is None:
            return
        details = details.lower()
        # The Wallet Unlocker gRPC service disappears from LND's API
        # after the wallet is unlocked (or created/recovered)
        if 'unknown service lnrpc.walletunlocker' in details:
            pass
        # User needs to create a new wallet
        elif 'wallet not found' in details:
            pass

    def auto_unlock_wallet(self):
        keyring_service_name = f'lnd_{self.node_set.bitcoin.network}_wallet_password'
        keyring_user_name = self.node_set.bitcoin.file['rpcuser']
        log.info(
            'auto_unlock_wallet_get_password',
            keyring_service_name=keyring_service_name,
            keyring_user_name=keyring_user_name
        )
        password = keyring.get_password(
            service=keyring_service_name,
            username=keyring_user_name,
        )
        if password is not None:
            worker = Worker(
                fn=self.unlock_wallet,
                lnd=self.node_set.lnd,
                password=password
            )
            worker.signals.result.connect(self.handle_unlock_wallet)
            self.threadpool.start(worker)

    def handle_output(self):
        output: QByteArray = self.process.readAllStandardOutput()
        message = output.data().decode('utf-8').strip()
        lines = message.split(os.linesep)
        for line in lines:
            self.output.append(line)
            if 'Waiting for wallet encryption password' in line:
                self.auto_unlock_wallet()
            elif 'Shutdown complete' in line:
                self.process.waitForFinished()
                self.process.start()
            elif 'LightningWallet opened' in line:
                self.system_tray.set_orange()
            elif 'Starting HTLC Switch' in line:
                self.system_tray.set_green()

    def show(self):
        self.showMaximized()
        self.raise_()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
