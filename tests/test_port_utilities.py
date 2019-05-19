import pytest

from node_launcher.port_utilities import is_port_in_use


@pytest.fixture
def used_port():
    port = 8000
    while port <= 65535:
        if is_port_in_use(port):
            return port
        port += 1


class TestBitcoinConfiguration(object):
    def test_is_port_in_use(self, used_port):
        assert is_port_in_use(used_port)
