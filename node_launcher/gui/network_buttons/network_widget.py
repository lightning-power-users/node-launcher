from PySide2 import QtWidgets
from PySide2.QtCore import QTimer, QThreadPool
from PySide2.QtWidgets import QWidget, QErrorMessage
# noinspection PyProtectedMember
from grpc._channel import _Rendezvous

from node_launcher.constants import keyring, MAINNET, Network
from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.network_buttons.cli_layout import CliLayout
from node_launcher.gui.network_buttons.joule_layout import JouleLayout
from node_launcher.gui.network_buttons.lnd_wallet_layout import \
    LndWalletLayout
from node_launcher.gui.network_buttons.nodes_layout import NodesLayout
from node_launcher.gui.network_buttons.zap_layout import ZapLayout
from node_launcher.gui.components.thread_worker import Worker
from node_launcher.node_set import NodeSet
from node_launcher.node_set.lnd import Lnd
from node_launcher.node_set.lnd_client import LndClient


class NetworkWidget(QtWidgets.QWidget):
    node_set: NodeSet
    timer = QTimer

    def __init__(self, parent: QWidget, network: Network = MAINNET):
        super().__init__(parent)

        self.timer = QTimer(self.parentWidget())

        self.node_set = NodeSet(network)

        columns = 2

        layout = QGridLayout()
        self.nodes_layout = NodesLayout(node_set=self.node_set)
        layout.addLayout(self.nodes_layout, column_span=columns)

        self.lnd_wallet_layout = LndWalletLayout(node_set=self.node_set,
                                                 parent=parent)
        layout.addLayout(self.lnd_wallet_layout, column_span=columns)

        self.zap_layout = ZapLayout(node_set=self.node_set)
        layout.addLayout(self.zap_layout, column_span=columns)

        self.joule_layout = JouleLayout(node_set=self.node_set)
        layout.addLayout(self.joule_layout, column_span=columns)

        self.cli_layout = CliLayout(node_set=self.node_set)
        layout.addLayout(self.cli_layout, column_span=columns)

        self.setLayout(layout)

        self.threadpool = QThreadPool()

        self.timer.start(1000)
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.refresh)

        self.refresh()

    def auto_unlock_wallet(self):
        password = keyring.get_password(
            service=f'lnd_{self.node_set.network}_wallet_password',
            username=self.node_set.bitcoin.file['rpcuser'],
        )
        if password is not None:
            worker = Worker(
                fn=self.lnd_poll,
                lnd=self.node_set.lnd,
                password=password
            )
            worker.signals.result.connect(self.handle_lnd_poll)
            self.threadpool.start(worker)
        else:
            self.set_lnd_wallet_unlock_state()

    def refresh(self):
        self.node_set.bitcoin.check_process()
        self.node_set.lnd.check_process()

        self.set_nodes_state()
        if self.node_set.lnd.running and not self.node_set.lnd.is_unlocked:
            if self.node_set.lnd.has_wallet:
                self.auto_unlock_wallet()
            else:
                self.set_lnd_wallet_create_recover_state()
        elif self.node_set.lnd.running and self.node_set.lnd.is_unlocked:
            self.set_lnd_wallet_open_state()
        elif not self.node_set.lnd.running:
            self.node_set.lnd.is_unlocked = False
            self.set_lnd_wallet_closed_state()
        self.set_zap_state()
        self.set_joule_state()
        self.set_cli_state()

    def set_cli_state(self):
        self.cli_layout.copy_bitcoin_cli.button.setEnabled(
            self.node_set.bitcoin.running
        )
        self.cli_layout.copy_lncli.button.setEnabled(
            self.node_set.lnd.is_unlocked
        )

    def set_joule_state(self):
        self.joule_layout.copy_rest.button.setEnabled(
            self.node_set.lnd.is_unlocked
        )
        self.joule_layout.show_macaroons.setEnabled(
            self.node_set.lnd.is_unlocked
        )

    def set_lnd_wallet_unlock_state(self):
        self.lnd_wallet_layout.create_wallet_button.setDisabled(True)
        self.lnd_wallet_layout.recover_wallet_button.setDisabled(True)
        self.lnd_wallet_layout.unlock_wallet_button.setDisabled(False)

    def set_lnd_wallet_create_recover_state(self):
        self.lnd_wallet_layout.create_wallet_button.setDisabled(False)
        self.lnd_wallet_layout.recover_wallet_button.setDisabled(False)
        self.lnd_wallet_layout.unlock_wallet_button.setDisabled(True)

    def set_lnd_wallet_open_state(self):
        self.lnd_wallet_layout.create_wallet_button.setDisabled(True)
        self.lnd_wallet_layout.recover_wallet_button.setDisabled(True)
        self.lnd_wallet_layout.unlock_wallet_button.setDisabled(True)

    def set_lnd_wallet_closed_state(self):
        self.lnd_wallet_layout.create_wallet_button.setDisabled(True)
        self.lnd_wallet_layout.recover_wallet_button.setDisabled(True)
        self.lnd_wallet_layout.unlock_wallet_button.setDisabled(True)

    def set_nodes_state(self):
        # Can not launch Bitcoin
        self.nodes_layout.bitcoin_qt_button.setDisabled(
            self.node_set.bitcoin.running
        )

        # Need to have Bitcoin running to launch LND
        disable_lnd_launch = (self.node_set.lnd.running
                              or not self.node_set.bitcoin.running)
        self.nodes_layout.lnd_button.setDisabled(disable_lnd_launch)

    def set_zap_state(self):
        self.zap_layout.open_zap_desktop_button.setEnabled(
            self.node_set.lnd.is_unlocked
        )
        self.zap_layout.show_zap_qrcode_button.setEnabled(
            self.node_set.lnd.is_unlocked
        )

    @staticmethod
    def lnd_poll(lnd: Lnd, progress_callback, password: str):
        client = LndClient(lnd)
        try:
            client.unlock(password)
        except _Rendezvous as e:
            details = e.details()
            return details

    def handle_lnd_poll(self, details: str):
        if details is None:
            return
        details = details.lower()
        if 'unknown service lnrpc.walletunlocker' in details:
            self.set_lnd_wallet_open_state()
        elif 'wallet not found' in details:
            self.set_lnd_wallet_create_recover_state()
        elif 'connect failed' in details:
            pass
        else:
            QErrorMessage(self).showMessage(details)
            self.set_lnd_wallet_open_state()
