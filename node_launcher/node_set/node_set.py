import os

from node_launcher.logging import log
from .bitcoin import Bitcoin
from .lnd import Lnd
from .tor import Tor


class NodeSet(object):
    bitcoin: Bitcoin
    lnd: Lnd
    tor: Tor

    def __init__(self):
        self.bitcoin = Bitcoin()
        self.lnd = Lnd(bitcoin=self.bitcoin)
        self.tor = Tor(lnd=self.lnd)
        self.tor.process.bootstrapped.connect(self.bitcoin.software.run)
        self.bitcoin.process.synced.connect(self.start_lnd)

    def start_lnd(self):
        hostname_file = os.path.join(self.tor.bitcoin_service_directory,
                                     'hostname')
        with open(hostname_file, 'r') as f:
            self.lnd.file['externalip'] = f.readline().strip()
        self.lnd.software.run()

    def run(self):
        log.debug('Starting node set')
        self.tor.software.run()
