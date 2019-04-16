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
        self.bitcoin.process.synced.connect(self.lnd.software.run)

    def run(self):
        self.tor.software.run()
