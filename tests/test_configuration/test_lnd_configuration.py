import os

import pytest

from node_launcher.configuration.lnd_configuration import (
    LndConfiguration
)
from node_launcher.utilities import is_port_in_use


@pytest.fixture
def lnd_configuration():
    lnd_configuration = LndConfiguration(network='testnet')
    return lnd_configuration


class TestDirectoryConfiguration(object):
    def test_lnd_data_path(self, lnd_configuration: LndConfiguration):
        assert os.path.isdir(lnd_configuration.lnddir)

    def test_rest(self, lnd_configuration: LndConfiguration):
        assert not is_port_in_use(lnd_configuration.rest_port)

    def test_node(self, lnd_configuration: LndConfiguration):
        assert not is_port_in_use(lnd_configuration.node_port)

    def test_grpc(self, lnd_configuration: LndConfiguration):
        assert not is_port_in_use(lnd_configuration.grpc_port)
