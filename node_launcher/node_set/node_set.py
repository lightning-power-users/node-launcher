import os

from node_launcher.logging import log
from node_launcher.node_set.bitcoin import Bitcoin
from node_launcher.node_set.lnd import Lnd
from node_launcher.constants import (
    BITCOIN_DATA_PATH,
    LND_DIR_PATH,
    OPERATING_SYSTEM,
)
from node_launcher.node_set.lnd_client import LndClient


class NodeSet(object):
    lnd_client: LndClient
    bitcoin: Bitcoin
    lnd: Lnd

    def __init__(self):
        file_name = 'bitcoin.conf'
        bitcoin_data_path = BITCOIN_DATA_PATH[OPERATING_SYSTEM]
        self.bitcoin_configuration_file_path = os.path.join(bitcoin_data_path,
                                                            file_name)
        log.info(
            'bitcoin_configuration_file_path',
            bitcoin_configuration_file_path=self.bitcoin_configuration_file_path
        )
        self.bitcoin = Bitcoin(
            configuration_file_path=self.bitcoin_configuration_file_path
        )

        file_name = 'lnd.conf'
        lnd_dir_path = LND_DIR_PATH[OPERATING_SYSTEM]
        self.lnd_configuration_file_path = os.path.join(lnd_dir_path, file_name)
        log.info(
            'lnd_configuration_file_path',
            lnd_configuration_file_path=self.lnd_configuration_file_path
        )
        self.lnd = Lnd(
            configuration_file_path=self.lnd_configuration_file_path,
            bitcoin=self.bitcoin
        )
        self.lnd_client = LndClient(self.lnd)

    @property
    def is_testnet(self) -> bool:
        return self.bitcoin.file['testnet']

    @property
    def is_mainnet(self) -> bool:
        return not self.bitcoin.file['testnet']

    def reset_tls(self):
        was_running = self.lnd.running
        if was_running:
            self.lnd.stop()
        os.remove(self.lnd_client.tls_cert_path)
        os.remove(self.lnd_client.tls_key_path)
        if was_running:
            self.lnd.launch()
        self.lnd_client.reset()
