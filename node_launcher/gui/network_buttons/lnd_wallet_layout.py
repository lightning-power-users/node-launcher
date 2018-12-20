import time

from PySide2 import QtWidgets
from PySide2.QtWidgets import QInputDialog, QLineEdit, QErrorMessage, QWidget
# noinspection PyProtectedMember
from grpc._channel import _Rendezvous

from node_launcher.constants import keyring
from node_launcher.gui.components.layouts import QGridLayout
from node_launcher.gui.horizontal_line import HorizontalLine
from node_launcher.gui.network_buttons.section_name import SectionName
from node_launcher.gui.seed_dialog import SeedDialog
from node_launcher.node_set import NodeSet


class LndWalletLayout(QGridLayout):
    node_set: NodeSet

    def __init__(self, parent: QWidget, node_set: NodeSet):
        super(LndWalletLayout, self).__init__()
        self.node_set = node_set
        self.password_dialog = QInputDialog(parent)
        self.error_message = QErrorMessage(parent)

        columns = 2
        self.addWidget(SectionName('LND Wallet'), column_span=columns)
        wallet_buttons_layout = QtWidgets.QHBoxLayout()
        # Unlock wallet button
        self.unlock_wallet_button = QtWidgets.QPushButton('Unlock')
        # noinspection PyUnresolvedReferences
        self.unlock_wallet_button.clicked.connect(self.unlock_wallet)
        wallet_buttons_layout.addWidget(self.unlock_wallet_button)

        # Create wallet button
        self.create_wallet_button = QtWidgets.QPushButton('Create')
        # noinspection PyUnresolvedReferences
        self.create_wallet_button.clicked.connect(self.create_wallet)
        wallet_buttons_layout.addWidget(self.create_wallet_button, same_row=True, column=2)

        # Recover wallet button
        self.recover_wallet_button = QtWidgets.QPushButton('Recover')
        # noinspection PyUnresolvedReferences
        self.recover_wallet_button.clicked.connect(self.recover_wallet)
        wallet_buttons_layout.addWidget(self.recover_wallet_button)
        self.addLayout(wallet_buttons_layout, column_span=columns)

        self.addWidget(HorizontalLine(), column_span=columns)

    def unlock_wallet(self):
        password, ok = QInputDialog.getText(self.password_dialog,
                                            f'Unlock {self.node_set.network} LND Wallet',
                                            'Wallet Password',
                                            QLineEdit.Password)
        if not ok:
            return
        try:
            self.node_set.lnd_client.unlock(wallet_password=password)
            keyring.set_password(
                service=f'lnd_{self.node_set.network}_wallet_password',
                username=str(time.time()),
                password=password)
        except _Rendezvous as e:
            # noinspection PyProtectedMember
            self.error_message.showMessage(e._state.details)
            return

        keyring.set_password(
            service=f'lnd_{self.node_set.network}_wallet_password',
            username=self.node_set.bitcoin.file['rpcuser'],
            password=password)


    def create_wallet(self):
        try:
            new_wallet_password, ok = QInputDialog.getText(self.password_dialog,
                                                           f'Create {self.node_set.network} LND Wallet',
                                                           'New Wallet Password',
                                                           QLineEdit.Password)
            if not ok:
                return

            seed_password, ok = QInputDialog.getText(self.password_dialog,
                                                     f'Create {self.node_set.network} LND Wallet',
                                                     'New Seed Password (Optional)',
                                                     QLineEdit.Password)
            if not ok:
                return
            if not seed_password:
                seed_password = None
            generate_seed_response = self.node_set.lnd_client.generate_seed(
                seed_password=seed_password)
            seed = generate_seed_response.cipher_seed_mnemonic

            seed_text = ''.join([f'{index + 1}: {value}\n' for index, value
                                 in enumerate(seed)])
            seed_dialog = SeedDialog()
            seed_dialog.text.setText(seed_text)
            seed_dialog.show()

            timestamp = str(time.time())
            keyring.set_password(
                service=f'lnd_{self.node_set.network}_wallet_password',
                username=timestamp,
                password=new_wallet_password)
            keyring.set_password(service=f'lnd_{self.node_set.network}_seed',
                                 username=timestamp,
                                 password=seed_text)
            if seed_password is not None:
                keyring.set_password(
                    service=f'lnd_{self.node_set.network}_seed_password',
                    username=timestamp,
                    password=seed_password)

            self.node_set.lnd_client.initialize_wallet(wallet_password=new_wallet_password,
                                                       seed=seed,
                                                       seed_password=seed_password)

        except _Rendezvous as e:
            # noinspection PyProtectedMember
            self.error_message.showMessage(e._state.details)
            return

        keyring.set_password(
            service=f'lnd_{self.node_set.network}_wallet_password',
            username=self.node_set.bitcoin.file['rpcuser'],
            password=new_wallet_password)

    def recover_wallet(self):
        try:
            new_wallet_password, ok = QInputDialog.getText(self.password_dialog,
                                                           f'Recover {self.node_set.network} LND Wallet',
                                                           'New Wallet Password',
                                                           QLineEdit.Password)
            if not ok:
                return

            seed_password, ok = QInputDialog.getText(self.password_dialog,
                                                     f'Recover {self.node_set.network} LND Wallet',
                                                     'Seed Password (Optional)',
                                                     QLineEdit.Password)
            if not ok:
                return
            if not seed_password:
                seed_password = None

            seed, ok = QInputDialog.getText(self.password_dialog,
                                            f'Recover {self.node_set.network} LND Wallet',
                                            'Seed')
            if not ok:
                return
            seed_list = seed.split(' ')

            timestamp = str(time.time())
            keyring.set_password(
                service=f'lnd_{self.node_set.network}_wallet_password',
                username=timestamp,
                password=new_wallet_password)
            keyring.set_password(service=f'lnd_{self.node_set.network}_seed',
                                 username=timestamp,
                                 password=seed)
            if seed_password is not None:
                keyring.set_password(
                    service=f'lnd_{self.node_set.network}_seed_password',
                    username=timestamp,
                    password=seed_password)

            self.node_set.lnd_client.initialize_wallet(wallet_password=new_wallet_password,
                                                       seed=seed_list,
                                                       seed_password=seed_password,
                                                       recovery_window=10000)
        except _Rendezvous as e:
            # noinspection PyProtectedMember
            self.error_message.showMessage(e._state.details)
            return

        keyring.set_password(
            service=f'lnd_{self.node_set.network}_wallet_password',
            username=self.node_set.bitcoin.file['rpcuser'],
            password=new_wallet_password)
