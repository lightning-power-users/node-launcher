import pytest
from tempfile import NamedTemporaryFile

from node_launcher.node_set.lnd import Lnd
from node_launcher.node_set.lnd_client import LndClient
from node_launcher.node_set import NodeSet
from node_launcher.node_set.bitcoin import Bitcoin
from node_launcher.gui.launch_widget import LaunchWidget


@pytest.fixture
def network() -> str:
    return 'testnet'


@pytest.fixture
def bitcoin(network: str) -> Bitcoin:
    with NamedTemporaryFile(suffix='-bitcoin.conf', delete=False) as f:
        bitcoin = Bitcoin(network=network,
                          configuration_file_path=f.name)
    return bitcoin


@pytest.fixture
def lnd(network: str, bitcoin: Bitcoin) -> Lnd:
    with NamedTemporaryFile(suffix='-lnd.conf', delete=False) as f:
        lnd = Lnd(network=network,
                  configuration_file_path=f.name,
                  bitcoin=bitcoin)
    return lnd


@pytest.fixture
def node_set(network: str,
             bitcoin: Bitcoin,
             lnd: Lnd) -> NodeSet:
    configuration = NodeSet(network)
    return configuration


@pytest.fixture
def lnd_client(lnd: Lnd) -> LndClient:
    lnd_client = LndClient(lnd)
    return lnd_client


@pytest.fixture
def launch_widget():
    launch_widget = LaunchWidget()
    return launch_widget
