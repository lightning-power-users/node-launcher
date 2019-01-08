import os

from node_launcher.node_set.bitcoin import Bitcoin
from node_launcher.node_set.lnd import Lnd
from node_launcher.constants import (
    BITCOIN_DATA_PATH,
    LND_DIR_PATH,
    MAINNET,
    Network,
    OPERATING_SYSTEM,
    TESTNET
)
from node_launcher.node_set.lnd_client import LndClient


class NodeSet(object):
    lnd_client: LndClient
    bitcoin: Bitcoin
    lnd: Lnd
    network: Network

    def __init__(self, network: Network):
        self.network = network

        self.bitcoin = Bitcoin(
            network=self.network,
            configuration_file_path=self.bitcoin_configuration_file_path
        )
        self.lnd = Lnd(
            network=self.network,
            configuration_file_path=self.lnd_configuration_file_path,
            bitcoin=self.bitcoin
        )
        self.lnd_client = LndClient(self.lnd)

    @property
    def is_testnet(self) -> bool:
        return self.network == TESTNET

    @property
    def is_mainnet(self) -> bool:
        return self.network == MAINNET

    @property
    def lnd_configuration_file_path(self) -> str:
        file_name = 'lnd.conf'
        if self.is_testnet:
            file_name = 'lnd-testnet.conf'
        lnd_dir_path = LND_DIR_PATH[OPERATING_SYSTEM]
        return os.path.join(lnd_dir_path, file_name)

    @property
    def bitcoin_configuration_file_path(self) -> str:
        file_name = 'bitcoin.conf'
        if self.is_testnet:
            file_name = 'bitcoin-testnet.conf'
        bitcoin_data_path = BITCOIN_DATA_PATH[OPERATING_SYSTEM]
        return os.path.join(bitcoin_data_path, file_name)

    def reset_tls(self):
        was_running = self.lnd.running
        if was_running:
            self.lnd.stop()
        os.remove(self.lnd_client.tls_cert_path)
        os.remove(self.lnd_client.tls_key_path)
        if was_running:
            self.lnd.launch()
        self.lnd_client.reset()
