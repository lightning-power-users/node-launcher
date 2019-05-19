from PySide2.QtCore import QThreadPool, QObject
from grpc._channel import _Rendezvous

from node_launcher.gui.components.thread_worker import Worker
from node_launcher.logging import log
from node_launcher.node_set.lib.get_random_password import get_random_password
from node_launcher.node_set.lnd.lnd_client import LndClient
from node_launcher.system_keyring import SystemKeyring


class LndUnlocker(QObject):
    def __init__(self, configuration):
        super().__init__()
        self.configuration = configuration
        self.client = LndClient(self.configuration)
        self.keyring = SystemKeyring()

    def auto_unlock_wallet(self):
        keyring_service_name = f'lnd_mainnet_wallet_password'
        keyring_user_name = self.configuration['bitcoind.rpcuser']
        log.info(
            'auto_unlock_wallet_get_password',
            keyring_service_name=keyring_service_name,
            keyring_user_name=keyring_user_name
        )
        password = self.keyring.get_password(
            service=keyring_service_name,
            username=keyring_user_name,
        )
        worker = Worker(
            fn=self.unlock_wallet,
            configuration=self.configuration,
            password=password
        )
        worker.signals.result.connect(self.handle_unlock_wallet)
        QThreadPool().start(worker)

    @staticmethod
    def unlock_wallet(configuration, password: str):
        if password is None:
            return 'wallet not found'
        client = LndClient(configuration)
        try:
            client.unlock(password)
            return None
        except _Rendezvous as e:
            details = e.details()
            return details

    def generate_seed(self, new_seed_password: str):
        try:
            generate_seed_response = self.client.generate_seed(
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

        self.keyring.set_password(
            service=keyring_service_name,
            username=keyring_user_name,
            password=' '.join(seed)
        )

        self.keyring.set_password(
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
            self.keyring.set_password(
                service=keyring_service_name,
                username=keyring_user_name,
                password=new_wallet_password
            )
            seed = self.generate_seed(new_wallet_password)
            try:
                self.client.initialize_wallet(
                    wallet_password=new_wallet_password,
                    seed=seed,
                    seed_password=new_wallet_password
                )
            except _Rendezvous:
                log.error('initialize_wallet error', exc_info=True)
                raise
            self.keyring.set_password(
                service=f'lnd_mainnet_wallet_password',
                username=self.configuration['bitcoind.rpcuser'],
                password=new_wallet_password
            )
        else:
            log.warning(
                'unlock_wallet failed',
                details=details,
                exc_info=True
            )
