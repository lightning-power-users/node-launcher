import time

import pytest

from node_launcher.node_set.bitcoind.bitcoind_rpc_client import Proxy, JSONRPCError
from node_launcher.node_set.lib.node_status import NodeStatus
from node_launcher.node_set.bitcoind.bitcoind_node import BitcoindNode
from node_launcher.node_set.tor.tor_node import TorNode


@pytest.fixture(scope='module')
def tor_node():
    return TorNode()


@pytest.fixture(scope='module')
def bitcoind_node():
    return BitcoindNode()


@pytest.fixture(scope='module')
def live_bitcoind_node(bitcoind_node: BitcoindNode, tor_node: TorNode, qtbot_session):
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
        return bitcoind_node.current_status == NodeStatus.SYNCED
    qtbot_session.waitUntil(check_synced, timeout=500000)
    return bitcoind_node


class TestBitcoindRpcClient(object):
    @pytest.mark.slow
    def test_get_raw_mempool(self, live_bitcoind_node: BitcoindNode, qtbot):
        client = Proxy(btc_conf_file=live_bitcoind_node.configuration.file.path,
                       service_port=live_bitcoind_node.configuration.rpc_port)
        while True:
            try:
                results = client.get_raw_mempool()
                total_fees = sum([r['fee'] for r in results])
                total_size = sum([r['size'] for r in results])
                total_count = len(results)
                assert results
                break
            except JSONRPCError as e:
                time.sleep(2)
                print(e)
        live_bitcoind_node.stop()

        def check_stopped():
            return live_bitcoind_node.current_status == NodeStatus.STOPPED
        qtbot.waitUntil(check_stopped, timeout=500000)