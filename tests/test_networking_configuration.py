import pytest

from node_launcher.networking_configuration import (
    NetworkingConfiguration,
    is_port_in_use
)


@pytest.fixture
def networking_configuration():
    networking_configuration = NetworkingConfiguration()
    return networking_configuration


@pytest.fixture
def used_port():
    port = 8000
    while port <= 65535:
        if is_port_in_use(port):
            return port
        port += 1


class TestNetworkingConfiguration(object):
    def test_is_port_in_use(self, used_port):
        assert is_port_in_use(used_port)

    def test_zmq_block_port(self, networking_configuration):
        assert not is_port_in_use(networking_configuration.zmq_block_port)

    def test_zmq_tx_port(self, networking_configuration):
        assert not is_port_in_use(networking_configuration.zmq_tx_port)

    def test_rest_port(self, networking_configuration):
        assert not is_port_in_use(networking_configuration.rest_port)

    def test_node_port(self, networking_configuration):
        assert not is_port_in_use(networking_configuration.node_port)

    def test_rpc_port(self, networking_configuration):
        assert not is_port_in_use(networking_configuration.grpc_port)
