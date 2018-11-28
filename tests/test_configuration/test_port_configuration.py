import pytest

from node_launcher.configuration.port_configuration import (
    PortConfiguration,
    is_port_in_use
)


@pytest.fixture
def port_configuration():
    port_configuration = PortConfiguration()
    return port_configuration


@pytest.fixture
def used_port():
    port = 8000
    while port <= 65535:
        if is_port_in_use(port):
            return port
        port += 1


class TestPortConfiguration(object):
    def test_is_port_in_use(self, used_port):
        assert is_port_in_use(used_port)

    def test_zmq_block(self, port_configuration):
        assert not is_port_in_use(port_configuration.zmq_block)

    def test_zmq_tx(self, port_configuration):
        assert not is_port_in_use(port_configuration.zmq_tx)

    def test_rest(self, port_configuration):
        assert not is_port_in_use(port_configuration.rest)

    def test_node(self, port_configuration):
        assert not is_port_in_use(port_configuration.node)

    def test_grpc(self, port_configuration):
        assert not is_port_in_use(port_configuration.grpc)
