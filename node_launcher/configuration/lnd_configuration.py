import os

from node_launcher.configuration.configuration_file import ConfigurationFile
from node_launcher.constants import LND_DIR_PATH, OPERATING_SYSTEM
from node_launcher.node_software.lnd_software import LndSoftware
from node_launcher.utilities import get_port


class LndConfiguration(object):
    file: ConfigurationFile
    software: LndSoftware

    def __init__(self, network: str, configuration_path: str = None):
        if configuration_path is None:
            configuration_path = os.path.join(LND_DIR_PATH[OPERATING_SYSTEM], 'lnd.conf')

        self.file = ConfigurationFile(configuration_path)
        self.software = LndSoftware()
        self.network = network

        self.lnddir = LND_DIR_PATH[OPERATING_SYSTEM]
        if not os.path.exists(self.lnddir):
            os.mkdir(self.lnddir)

        # LND
        self.rest_port = get_port(8080)
        self.node_port = get_port(9735)
        self.grpc_port = get_port(10009)

    @property
    def macaroon_path(self) -> str:
        macaroons_path = os.path.join(self.lnddir, 'data', 'chain', 'bitcoin', self.network)
        return macaroons_path

    @property
    def tls_cert_path(self) -> str:
        tls_cert_path = os.path.join(self.lnddir, 'tls.cert')
        return tls_cert_path
