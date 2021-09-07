from grpc._channel import _Rendezvous

from node_launcher.gui.qt import QObject
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

    @property
    def keyring_service_name(self):
        return f'lnd_mainnet_wallet_password'

    def get_password(self):
        for service_name in [self.keyring_service_name, 'lnd_wallet_password']:
            for user_name in [self.keyring_service_name, self.configuration['bitcoind.rpcuser'], 'lnd_wallet_password']:
                log.info(
                    'auto_unlock_wallet_get_password',
                    keyring_service_name=service_name,
                    keyring_user_name=user_name
                )
                password = self.keyring.get_password(
                    service=service_name,
                    username=user_name,
                )
                if password is not None:
                    log.info(
                        'Successfully got password from',
                        keyring_service_name=service_name,
                        keyring_user_name=user_name
                    )
                    yield password

    def auto_unlock_wallet(self):
        for password in self.get_password():
            error = self.unlock_wallet(
                configuration=self.configuration,
                password=password
            )
            if error is None:
                return
        self.handle_unlock_wallet('wallet not found')

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

        keyring_user_name = ''.join(seed[0:2])
        log.info(
            'generate_seed',
            keyring_service_name=self.keyring_service_name,
            keyring_user_name=keyring_user_name
        )

        self.keyring.set_password(
            service=self.keyring_service_name,
            username=keyring_user_name,
            password=' '.join(seed)
        )

        self.keyring.set_password(
            service=f'{self.keyring_service_name}_seed_password',
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
            log.info(
                'create_wallet',
                keyring_service_name=self.keyring_service_name,
                keyring_user_name=self.keyring_service_name
            )
            self.keyring.set_password(
                service=self.keyring_service_name,
                username=self.keyring_service_name,
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
                service=self.keyring_service_name,
                username=self.keyring_service_name,
                password=new_wallet_password
            )
        elif 'invalid passphrase for master public key' in details:
            self.system_tray.menu.lnd_status_action.setText(
                'Invalid LND Password'
            )
        else:
            log.warning(
                'unlock_wallet failed',
                details=details,
                exc_info=True
            )
