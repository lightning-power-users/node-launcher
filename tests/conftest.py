import pytest

from node_launcher.node_set.lnd.lnd import Lnd
from node_launcher.node_set.lnd.lnd_client import LndClient


@pytest.fixture
def lnd_client(lnd: Lnd) -> LndClient:
    lnd_client = LndClient(lnd)
    return lnd_client

