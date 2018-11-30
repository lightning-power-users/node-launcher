import os
import subprocess
import sys

from PySide2 import QtWidgets
from PySide2.QtGui import QClipboard
from PySide2.QtWidgets import QErrorMessage

from node_launcher.constants import LINUX, OPERATING_SYSTEM, DARWIN, IS_WINDOWS
from node_launcher.gui.horizontal_line import HorizontalLine
from node_launcher.gui.image_label import ImageLabel
from node_launcher.node_launcher import NodeLauncher
from node_launcher.utilities import reveal


class NetworkGroupBox(QtWidgets.QGroupBox):
    network: str
    node_launcher: NodeLauncher

    def __init__(self, network: str, node_launcher: NodeLauncher):
        super().__init__(network)
        self.network = network
        self.node_launcher = node_launcher

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(ImageLabel(f'bitcoin-{network}.png'))
        layout.addStretch(1)

        self.error_message = QErrorMessage(self)
        if OPERATING_SYSTEM == LINUX:
            self.error_message.showMessage('Linux is not supported, please submit a pull request! '
                                           'https://github.com/PierreRochard/node-launcher')
            sys.exit(0)

        layout.addWidget(HorizontalLine())

        # Bitcoin-Qt button
        self.bitcoin_qt_button = QtWidgets.QPushButton('Launch Bitcoin')
        bitcoin_qt_launcher = getattr(node_launcher, f'{network}_bitcoin_qt_node')
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

        # Copy REST API URL button
        self.rest_url_copy_button = QtWidgets.QPushButton('Copy LND REST Address')
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
                                 self.network).dir.macaroon_path(self.network)
        reveal(macaroons_path)

    def copy_lncli_command(self):
        command = getattr(self.node_launcher.command_generator,
                          f'{self.network}_lncli')()
        QClipboard().setText(' '.join(command))

    def copy_rest_url(self):
        rest_url = getattr(self.node_launcher.command_generator,
                           f'{self.network}_rest_url')()
        QClipboard().setText(rest_url)
