import os
import uuid
from datetime import datetime

import humanize
from PySide2.QtCore import QByteArray, QThreadPool, QProcess, Qt, QTimer
from PySide2.QtWidgets import QDialog, QTextEdit
from grpc._channel import _Rendezvous

from node_launcher.constants import keyring
from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.thread_worker import Worker
from node_launcher.logging import log
from node_launcher.node_set import NodeSet
from node_launcher.node_set.lnd_client import LndClient


class LndOutputWidget(QDialog):
    node_set: NodeSet
    process: QProcess

    def __init__(self, node_set: NodeSet, system_tray):
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

        self.old_height = None
        self.old_timestamp = None

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
            return details

    def generate_seed(self, new_seed_password: str):
        try:
            generate_seed_response = self.node_set.lnd_client.generate_seed(
                seed_password=new_seed_password
            )
        except _Rendezvous as e:
            log.error(
                'generate_seed',
                exc_info=True
            )
            # noinspection PyProtectedMember
            self.error_message.showMessage(e._state.details)
            return

        seed = generate_seed_response.cipher_seed_mnemonic

        keyring_service_name = f'lnd_seed'
        keyring_user_name = ''.join(seed[0:2])
        log.info(
            'generate_seed',
            keyring_service_name=keyring_service_name,
            keyring_user_name=keyring_user_name
        )

        keyring.set_password(
            service=keyring_service_name,
            username=keyring_user_name,
            password=' '.join(seed)
        )

        if new_seed_password is not None:
            keyring.set_password(
                service=f'{keyring_service_name}_password',
                username=keyring_user_name,
                password=new_seed_password
            )
        return seed

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
            new_wallet_password = uuid.uuid4().hex
            keyring_service_name = keyring_user_name = f'lnd_wallet_password'
            log.info(
                'create_wallet',
                keyring_service_name=keyring_service_name,
                keyring_user_name=keyring_user_name
            )
            keyring.set_password(
                service=keyring_service_name,
                username=keyring_user_name,
                password=new_wallet_password
            )
            seed = self.generate_seed(new_wallet_password)
            try:
                self.node_set.lnd_client.initialize_wallet(
                    wallet_password=new_wallet_password,
                    seed=seed,
                    seed_password=new_wallet_password
                )
            except _Rendezvous as e:
                log.error(
                    'initialize_wallet',
                    exc_info=True
                )
                # noinspection PyProtectedMember
                self.error_message.showMessage(e._state.details)
                return
            keyring.set_password(
                service=f'lnd_{self.node_set.bitcoin.network}_wallet_password',
                username=self.node_set.bitcoin.file['rpcuser'],
                password=new_wallet_password
            )
        else:
            log.warning(
                'unlock_wallet failed',
                details=details,
                exc_info=True
            )

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
            if 'Active chain: Bitcoin' in line:
                self.system_tray.menu.lnd_status_action.setText(
                    'LND starting...'
                )
            elif 'Waiting for wallet encryption password' in line:
                self.system_tray.menu.lnd_status_action.setText(
                    'LND unlocking wallet...'
                )
                self.auto_unlock_wallet()
            elif 'Shutdown complete' in line:
                self.process.waitForFinished()
                QTimer.singleShot(1500, self.process.start)
            elif 'Unable to synchronize wallet to chain' in line:
                self.process.terminate()
                self.process.waitForFinished()
                self.process.start()
                self.process.waitForStarted()
            elif 'LightningWallet opened' in line:
                self.system_tray.set_orange()
                self.system_tray.menu.lnd_status_action.setText(
                    'LND syncing with network...'
                )
            elif 'Starting HTLC Switch' in line:
                self.system_tray.set_green()
                self.system_tray.menu.lnd_status_action.setText(
                    'LND synced'
                )
            elif 'Caught up to height' in line:
                new_height = int(line.split(' ')[-1])
                timestamp = line.split('[INF]')[0].strip()
                new_timestamp = datetime.strptime(
                    timestamp,
                    '%Y-%m-%d %H:%M:%S.%f'
                )
                if self.old_height is not None:
                    change = new_height - self.old_height
                    timestamp_change = new_timestamp - self.old_timestamp
                    total_left = 600000 - new_height
                    time_left = (total_left / change)*timestamp_change
                    humanized = humanize.naturaltime(-time_left)
                    self.system_tray.menu.lnd_status_action.setText(
                        f'ETA: {humanized}, caught up to height {new_height}'
                    )

                self.old_height = new_height
                self.old_timestamp = new_timestamp



    def show(self):
        self.showMaximized()
        self.raise_()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
