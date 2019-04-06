from datetime import datetime

# noinspection PyPackageRequirements
from grpc._channel import _Rendezvous
import humanize
from PySide2.QtCore import QThreadPool, Qt, QTimer

from node_launcher.constants import keyring
from node_launcher.gui.components.thread_worker import Worker
from node_launcher.gui.components.output_widget import OutputWidget
from node_launcher.logging import log
from node_launcher.node_set import NodeSet
from node_launcher.node_set.lnd_client import LndClient
from node_launcher.utilities.utilities import get_random_password


class LndOutputWidget(OutputWidget):
    def __init__(self, node_set: NodeSet, system_tray):
        super().__init__()
        self.node_set = node_set
        self.system_tray = system_tray
        self.process = node_set.lnd.process
        self.process.readyReadStandardError.connect(self.handle_error)
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.setWindowTitle('LND Output')

        self.threadpool = QThreadPool()

        self.old_height = None
        self.old_timestamp = None
        self.process.errorOccurred.connect(self.restart_process)
        self.process.finished.connect(self.restart_process)

    def process_output_line(self, line: str):
        if 'Active chain: Bitcoin' in line:
            self.system_tray.menu.lnd_status_action.setText(
                'LND starting'
            )
        elif 'Waiting for wallet encryption password' in line:
            self.system_tray.menu.lnd_status_action.setText(
                'LND unlocking wallet'
            )
            QTimer.singleShot(100, self.auto_unlock_wallet)
        elif 'Unable to synchronize wallet to chain' in line:
            self.process.terminate()
        elif 'Unable to complete chain rescan' in line:
            self.process.terminate()
        elif 'Starting HTLC Switch' in line:
            self.system_tray.set_green()
            self.system_tray.menu.lnd_status_action.setText(
                'LND synced'
            )
            self.system_tray.showMessage(
                'Lightning is ready',
                ''
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
                if change:
                    timestamp_change = new_timestamp - self.old_timestamp
                    total_left = 600000 - new_height
                    time_left = (total_left / change)*timestamp_change
                    humanized = humanize.naturaltime(-time_left)
                    self.system_tray.menu.lnd_status_action.setText(
                        f'ETA: {humanized}, caught up to height {new_height}'
                    )

            self.old_height = new_height
            self.old_timestamp = new_timestamp

    def restart_process(self):
        QTimer.singleShot(3000, self.process.start)

    @staticmethod
    def unlock_wallet(lnd, progress_callback, password: str):
        if password is None:
            return 'wallet not found'
        client = LndClient(lnd)
        try:
            client.unlock(password)
            return None
        except _Rendezvous as e:
            details = e.details()
            return details

    def generate_seed(self, new_seed_password: str):
        try:
            generate_seed_response = self.node_set.lnd_client.generate_seed(
                seed_password=new_seed_password
            )
        except _Rendezvous:
            log.error('generate_seed error', exc_info=True)
            raise

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

        keyring.set_password(
            service=f'{keyring_service_name}_seed_password',
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
            new_wallet_password = get_random_password()
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
            except _Rendezvous:
                log.error('initialize_wallet error', exc_info=True)
                raise
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
        worker = Worker(
            fn=self.unlock_wallet,
            lnd=self.node_set.lnd,
            password=password
        )
        worker.signals.result.connect(self.handle_unlock_wallet)
        self.threadpool.start(worker)

    def show(self):
        self.showMaximized()
        self.raise_()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
