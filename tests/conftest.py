import pytest
from tempfile import NamedTemporaryFile

from node_launcher.constants import Network, TESTNET
from node_launcher.node_set.lnd import Lnd
from node_launcher.node_set.lnd_client import LndClient
from node_launcher.node_set import NodeSet
from node_launcher.node_set.bitcoin import Bitcoin
from node_launcher.node_set.tor import Tor
from node_launcher.gui.main_widget import MainWidget


@pytest.fixture
def network() -> Network:
    return TESTNET


@pytest.fixture
def bitcoin(network: str) -> Bitcoin:
    with NamedTemporaryFile(suffix='-bitcoin.conf', delete=False) as f:
        bitcoin = Bitcoin(configuration_file_path=f.name)
    return bitcoin


@pytest.fixture
def lnd(network: str, bitcoin: Bitcoin) -> Lnd:
    with NamedTemporaryFile(suffix='-lnd.conf', delete=False) as f:
        lnd = Lnd(configuration_file_path=f.name,
                  bitcoin=bitcoin)
    return lnd

@pytest.fixture
def tor(network: str, lnd: Lnd) -> Tor:
    with NamedTemporaryFile(suffix='-torrc', delete=False) as f:
        tor = Tor(configuration_file_path=f.name,
                  lnd=lnd)
    return tor


@pytest.fixture
def node_set(network: str,
             bitcoin: Bitcoin,
             lnd: Lnd,
             tor: Tor) -> NodeSet:
    configuration = NodeSet()
    return configuration


@pytest.fixture
def lnd_client(lnd: Lnd) -> LndClient:
    lnd_client = LndClient(lnd)
    return lnd_client


@pytest.fixture
def main_widget():
    main_widget = MainWidget()
    return main_widget
