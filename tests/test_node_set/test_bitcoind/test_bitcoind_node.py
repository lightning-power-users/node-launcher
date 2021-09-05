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
            if status in [NodeStatus.SOFTWARE_DOWNLOADED,
                          NodeStatus.SOFTWARE_READY]:
                bitcoind_node.software.update()
            elif status == NodeStatus.SYNCED:
                bitcoind_node.tor_synced = True
                bitcoind_node.start_process()

        tor_node.status.connect(handle_tor_node_status_change)
        tor_node.software.update()

        def check_synced():
            return bitcoind_node.current_status == NodeStatus.SYNCING
        qtbot.waitUntil(check_synced, timeout=500000)
        bitcoind_node.stop()

        def check_stopped():
            return bitcoind_node.current_status == NodeStatus.STOPPED
        qtbot.waitUntil(check_stopped, timeout=500000)
