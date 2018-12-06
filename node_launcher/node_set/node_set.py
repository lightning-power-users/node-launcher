import os

from node_launcher.node_set.bitcoin import \
    Bitcoin
from node_launcher.node_set.lnd import Lnd
from node_launcher.constants import LND_DIR_PATH, OPERATING_SYSTEM, BITCOIN_DATA_PATH
from node_launcher.node_set.lnd_client import LndClient


class NodeSet(object):

    lnd_client: LndClient
    bitcoin: Bitcoin
    lnd: Lnd
    network: str

    def __init__(self, network: str):
        self.network = network
        self.lnd_configuration_file_path = os.path.join(LND_DIR_PATH[OPERATING_SYSTEM],
                                                        'lnd.conf')

        self.bitcoin_configuration_file_path = os.path.join(BITCOIN_DATA_PATH[OPERATING_SYSTEM],
                                                            'bitcoin.conf')

        self.bitcoin = Bitcoin(network=self.network,
                               configuration_file_path=self.bitcoin_configuration_file_path)
        self.lnd = Lnd(network=self.network,
                       configuration_file_path=self.lnd_configuration_file_path,
                       bitcoin=self.bitcoin)
        self.lnd_client = LndClient(self.lnd)
