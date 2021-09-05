import pytest

from node_launcher.node_set.lib.node_status import NodeStatus
from node_launcher.node_set.bitcoind.bitcoind_node import BitcoindNode
from node_launcher.node_set.lnd.lnd_node import LndNode
from node_launcher.node_set.tor.tor_node import TorNode


@pytest.fixture
def tor_node():
    return TorNode()


@pytest.fixture
def bitcoind_node():
    return BitcoindNode()


@pytest.fixture()
def lnd_node():
    return LndNode()


class TestLndNode(object):
    @pytest.mark.slow
    def test_start(self, tor_node: TorNode, bitcoind_node: BitcoindNode,
                   lnd_node: LndNode, qtbot):

        def handle_tor_status(status):
            if status in [NodeStatus.SOFTWARE_DOWNLOADED,
                          NodeStatus.SOFTWARE_READY]:
                bitcoind_node.software.update()
            elif status == NodeStatus.SYNCED:
                bitcoind_node.tor_synced = True
                bitcoind_node.start_process()
        tor_node.status.connect(handle_tor_status)

        def handle_bitcoind_status(status):
            if status in [NodeStatus.SOFTWARE_DOWNLOADED,
                          NodeStatus.SOFTWARE_READY]:
                lnd_node.software.update()
            elif status == NodeStatus.SYNCING:
                lnd_node.bitcoind_syncing = True
                lnd_node.start_process()
            elif status == NodeStatus.STOPPED:
                tor_node.stop()
        bitcoind_node.status.connect(handle_bitcoind_status)

        def handle_lnd_status(status):
            if status == NodeStatus.SYNCING:
                lnd_node.stop()
            elif status == NodeStatus.STOPPED:
                bitcoind_node.stop()
        lnd_node.status.connect(handle_lnd_status)

        tor_node.software.update()

        def check_synced():
            return lnd_node.current_status == NodeStatus.SYNCING
        qtbot.waitUntil(check_synced, timeout=5000000)

        lnd_node.stop()

        def check_stopped():
            return tor_node.current_status == NodeStatus.STOPPED
        qtbot.waitUntil(check_stopped, timeout=5000000)
