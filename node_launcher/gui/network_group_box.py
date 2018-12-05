import sys

from PySide2 import QtWidgets
from PySide2.QtGui import QClipboard
from PySide2.QtWidgets import QErrorMessage, QInputDialog, QLineEdit
from grpc._channel import _Rendezvous

from node_launcher.constants import LINUX, OPERATING_SYSTEM
from node_launcher.gui.horizontal_line import HorizontalLine
from node_launcher.gui.image_label import ImageLabel
from node_launcher.gui.seed_dialog import SeedDialog
from node_launcher.lnd_client.lnd_client import LndClient
from node_launcher.node_launcher import NodeLauncher
from node_launcher.utilities import reveal


class NetworkGroupBox(QtWidgets.QGroupBox):
    lnd_client: LndClient
    network: str
    node_launcher: NodeLauncher

    def __init__(self, network: str, node_launcher: NodeLauncher):
        super().__init__(network)
        self.network = network
        self.node_launcher = node_launcher
        self.password_dialog = QInputDialog(self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(ImageLabel(f'bitcoin-{network}.png'))
        layout.addStretch(1)

        self.error_message = QErrorMessage(self)
        if OPERATING_SYSTEM == LINUX:
            self.error_message.showMessage(
                'Linux is not supported, please submit a pull request! '
                'https://github.com/PierreRochard/node-launcher')
            sys.exit(0)

        layout.addWidget(HorizontalLine())

        # Bitcoin-Qt button
        self.bitcoin_qt_button = QtWidgets.QPushButton('Launch Bitcoin')
        bitcoin_qt_launcher = getattr(node_launcher,
                                      f'{network}_bitcoin_qt_node')
        # noinspection PyUnresolvedReferences
        self.bitcoin_qt_button.clicked.connect(bitcoin_qt_launcher)
        layout.addWidget(self.bitcoin_qt_button)

        # LND button
        self.lnd_button = QtWidgets.QPushButton('Launch LND')
        lnd_launcher = getattr(node_launcher, f'{network}_lnd_node')
        # noinspection PyUnresolvedReferences
        self.lnd_button.clicked.connect(lnd_launcher)
        layout.addWidget(self.lnd_button)

        layout.addWidget(HorizontalLine())

        # Unlock button
        self.unlock_wallet_button = QtWidgets.QPushButton('Unlock Wallet')
        # noinspection PyUnresolvedReferences
        self.unlock_wallet_button.clicked.connect(self.unlock_wallet)
        layout.addWidget(self.unlock_wallet_button)

        # Initialize wallet button
        self.initialize_wallet_button = QtWidgets.QPushButton('Initialize Wallet')
        # noinspection PyUnresolvedReferences
        self.initialize_wallet_button.clicked.connect(self.initialize_wallet)
        layout.addWidget(self.initialize_wallet_button)

        # Recover wallet button
        self.recover_wallet_button = QtWidgets.QPushButton('Recover Wallet')
        # noinspection PyUnresolvedReferences
        self.recover_wallet_button.clicked.connect(self.recover_wallet)
        layout.addWidget(self.recover_wallet_button)

        layout.addWidget(HorizontalLine())

        # Copy REST API URL button
        self.rest_url_copy_button = QtWidgets.QPushButton(
            'Copy LND REST Address')
        # noinspection PyUnresolvedReferences
        self.rest_url_copy_button.clicked.connect(self.copy_rest_url)
        layout.addWidget(self.rest_url_copy_button)

        # Show Macaroons button
        self.show_macaroons_button = QtWidgets.QPushButton('Show Macaroons')
        # noinspection PyUnresolvedReferences
        self.show_macaroons_button.clicked.connect(self.reveal_macaroons)
        layout.addWidget(self.show_macaroons_button)

        # Copy lncli command button
        self.lncli_copy_button = QtWidgets.QPushButton('Copy lncli Command')
        # noinspection PyUnresolvedReferences
        self.lncli_copy_button.clicked.connect(self.copy_lncli_command)
        layout.addWidget(self.lncli_copy_button)

        self.setLayout(layout)

    def reveal_macaroons(self):
        macaroons_path = getattr(self.node_launcher.command_generator,
                                 self.network).lnd.macaroon_path
        try:
            reveal(macaroons_path)
        except (FileNotFoundError, NotADirectoryError):
            self.error_message.showMessage(f'{macaroons_path} not found')
            return

    def copy_lncli_command(self):
        command = getattr(self.node_launcher.command_generator,
                          f'{self.network}_lncli')()
        QClipboard().setText(' '.join(command))

    def copy_rest_url(self):
        rest_url = getattr(self.node_launcher.command_generator,
                           f'{self.network}_rest_url')()
        QClipboard().setText(rest_url)

    def unlock_wallet(self):
        password, ok = QInputDialog.getText(self.password_dialog,
                                            f'Unlock {self.network} LND Wallet',
                                            'Wallet Password',
                                            QLineEdit.Password)
        if not ok:
            return
        try:
            self.node_launcher.unlock_wallet(network=self.network, wallet_password=password)
        except _Rendezvous as e:
            self.error_message.showMessage(e._state.details)
            return

    def initialize_wallet(self):
        try:
            new_wallet_password, ok = QInputDialog.getText(self.password_dialog,
                                                           f'Initialize {self.network} LND Wallet',
                                                           'New Wallet Password',
                                                           QLineEdit.Password)
            if not ok:
                return

            seed_password, ok = QInputDialog.getText(self.password_dialog,
                                                     f'Initialize {self.network} LND Wallet',
                                                     'New Seed Password (Optional)',
                                                     QLineEdit.Password)
            if not ok:
                return
            if not seed_password:
                seed_password = None
            generate_seed_response = self.node_launcher.generate_seed(network=self.network,
                                                                      seed_password=seed_password)

            seed_text = ''.join([f'{index + 1}: {value}\n' for index, value
                                 in enumerate(generate_seed_response)])
            seed_dialog = SeedDialog()
            seed_dialog.text.setText(seed_text)
            seed_dialog.show()
            self.node_launcher.initialize_wallet(network=self.network,
                                                 wallet_password=new_wallet_password,
                                                 seed=generate_seed_response,
                                                 seed_password=seed_password)

        except _Rendezvous as e:
            # noinspection PyProtectedMember
            self.error_message.showMessage(e._state.details)
            return

    def recover_wallet(self):
        try:
            new_wallet_password, ok = QInputDialog.getText(self.password_dialog,
                                                           f'Restore {self.network} LND Wallet',
                                                           'New Wallet Password',
                                                           QLineEdit.Password)
            if not ok:
                return

            seed_password, ok = QInputDialog.getText(self.password_dialog,
                                                     f'Restore {self.network} LND Wallet',
                                                     'Seed Password (Optional)',
                                                     QLineEdit.Password)
            if not ok:
                return
            if not seed_password:
                seed_password = None

            seed, ok = QInputDialog.getText(self.password_dialog,
                                            f'Initialize {self.network} LND Wallet',
                                            'Seed')
            if not ok:
                return
            seed_list = seed.split(' ')

            self.node_launcher.initialize_wallet(network=self.network,
                                                 wallet_password=new_wallet_password,
                                                 seed=seed_list,
                                                 seed_password=seed_password,
                                                 recovery_window=10000)
        except _Rendezvous as e:
            # noinspection PyProtectedMember
            self.error_message.showMessage(e._state.details)
            return
