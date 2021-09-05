import pytest

from node_launcher.node_set.lib.node_status import NodeStatus
from node_launcher.node_set.tor.tor_node import TorNode


@pytest.fixture
def tor_node():
    return TorNode()


class TestTorNode(object):
    @pytest.mark.slow
    def test_start(self, tor_node: TorNode, qtbot):
        tor_node.software.update()

        def check_status():
            return tor_node.current_status == str(NodeStatus.SYNCED)
        qtbot.waitUntil(check_status, timeout=5000)
        tor_node.stop()

