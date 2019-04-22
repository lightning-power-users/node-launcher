import pytest

from node_launcher.node_set.lib.node_status import NodeStatus
from node_launcher.node_set.bitcoind.bitcoind_node import BitcoindNode
from node_launcher.node_set.tor.tor_node import TorNode


@pytest.fixture
def tor_node():
    return TorNode()


@pytest.fixture
def bitcoind_node():
    return BitcoindNode()


class TestBitcoindNode(object):
    @pytest.mark.slow
    def test_start(self, bitcoind_node: BitcoindNode, tor_node: TorNode, qtbot):

        def handle_tor_node_status_change(status):
            if status == str(NodeStatus.SYNCED):
                bitcoind_node.start()

        tor_node.status.connect(handle_tor_node_status_change)
        tor_node.start()

        def check_synced():
            return bitcoind_node.current_status == str(NodeStatus.SYNCING)
        qtbot.waitUntil(check_synced, timeout=50000)
        bitcoind_node.stop()

        def check_stopped():
            return bitcoind_node.current_status == str(NodeStatus.STOPPED)
        qtbot.waitUntil(check_stopped, timeout=50000)
