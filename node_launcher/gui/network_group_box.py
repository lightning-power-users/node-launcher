import sys
import time

from PySide2 import QtWidgets
from PySide2.QtGui import QClipboard
from PySide2.QtWidgets import QErrorMessage, QInputDialog, QLineEdit, QLabel
from grpc._channel import _Rendezvous

from node_launcher.gui.components.layouts import QGridLayout
from node_launcher.node_set import NodeSet
from node_launcher.constants import LINUX, OPERATING_SYSTEM, keyring
from node_launcher.gui.horizontal_line import HorizontalLine
from node_launcher.gui.image_label import ImageLabel
from node_launcher.gui.seed_dialog import SeedDialog
from node_launcher.utilities import reveal


class SectionName(QLabel):
    def __init__(self, text: str):
        super().__init__()
        self.setText(text)


class NetworkGroupBox(QtWidgets.QGroupBox):
    node_set: NodeSet

    def __init__(self, network: str = 'mainnet'):
        super().__init__(network)
        self.password_dialog = QInputDialog(self)
        self.error_message = QErrorMessage(self)

        self.node_set = NodeSet(network)

        columns = 2

        layout = QGridLayout()
        image_label = ImageLabel(f'bitcoin-{network}.png')
        layout.addWidget(image_label, row_span=5)

        if OPERATING_SYSTEM == LINUX:
            self.error_message.showMessage(
                'Linux is not supported, please submit a pull request! '
                'https://github.com/PierreRochard/node-launcher')
            sys.exit(0)

        layout.addWidget(SectionName('Nodes'), column=columns)
        # Bitcoin-Qt button
        self.bitcoin_qt_button = QtWidgets.QPushButton('Launch Bitcoin')
        # noinspection PyUnresolvedReferences
        self.bitcoin_qt_button.clicked.connect(self.node_set.bitcoin.launch)
        layout.addWidget(self.bitcoin_qt_button, column=columns)

        # LND button
        self.lnd_button = QtWidgets.QPushButton('Launch LND')
        # noinspection PyUnresolvedReferences
        self.lnd_button.clicked.connect(self.node_set.lnd.launch)
        layout.addWidget(self.lnd_button, column=columns)

        layout.addWidget(HorizontalLine(), column=columns)

        layout.addWidget(SectionName('LND Wallet'), column_span=columns)
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
        layout.addLayout(wallet_buttons_layout, column_span=columns)
        layout.addWidget(HorizontalLine(), column_span=columns)

        layout.addWidget(SectionName('Zap'), column_span=columns)
        # Copy gRPC API URL button
        self.grpc_url_copy_button = QtWidgets.QPushButton(
            'Copy LND gRPC Address')
        # noinspection PyUnresolvedReferences
        self.grpc_url_copy_button.clicked.connect(self.copy_grpc_url)
        layout.addWidget(self.grpc_url_copy_button)

        # Copy REST API URL button
        self.rest_url_copy_button = QtWidgets.QPushButton(
            'Copy LND REST Address')
        # noinspection PyUnresolvedReferences
        self.rest_url_copy_button.clicked.connect(self.copy_rest_url)
        layout.addWidget(self.rest_url_copy_button, same_row=True, column=2)

        layout.addWidget(HorizontalLine(), column_span=3)

        layout.addWidget(SectionName('Joule'), column_span=3)

        # Show Macaroons button
        self.show_macaroons_button = QtWidgets.QPushButton('Show Macaroons')
        # noinspection PyUnresolvedReferences
        self.show_macaroons_button.clicked.connect(self.reveal_macaroons)
        layout.addWidget(self.show_macaroons_button)

        # Copy lncli command button
        self.lncli_copy_button = QtWidgets.QPushButton('Copy lncli Command')
        # noinspection PyUnresolvedReferences
        self.lncli_copy_button.clicked.connect(self.copy_lncli_command)
        layout.addWidget(self.lncli_copy_button, same_row=True, column=2)

        self.setLayout(layout)

    def reveal_macaroons(self):
        try:
            reveal(self.node_set.lnd.macaroon_path)
        except (FileNotFoundError, NotADirectoryError):
            self.error_message.showMessage(f'{self.node_set.lnd.macaroon_path} not found')
            return

    def copy_lncli_command(self):
        QClipboard().setText(' '.join(self.node_set.lnd.lncli))

    def copy_rest_url(self):
        QClipboard().setText(self.node_set.lnd.rest_url)

    def copy_grpc_url(self):
        QClipboard().setText(self.node_set.lnd.grpc_url)

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

            seed_text = ''.join([f'{index + 1}: {value}\n' for index, value
                                 in enumerate(generate_seed_response)])
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
                                                       seed=generate_seed_response,
                                                       seed_password=seed_password)

        except _Rendezvous as e:
            # noinspection PyProtectedMember
            self.error_message.showMessage(e._state.details)
            return

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
