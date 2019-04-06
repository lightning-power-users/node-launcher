from unittest.mock import MagicMock

import pytest
from PySide2.QtTest import QTest

from node_launcher.constants import (
    BITCOIN_MAINNET_PEER_PORT,
    LND_DEFAULT_PEER_PORT,
    BITCOIN_MAINNET_RPC_PORT,
    LND_DEFAULT_GRPC_PORT,
    LND_DEFAULT_REST_PORT
)
from node_launcher.gui.menu import PortsLayout


@pytest.fixture
def ports_layout():
    node_set = MagicMock()
    node_set.bitcoin.node_port = BITCOIN_MAINNET_PEER_PORT
    node_set.bitcoin.rpc_port = BITCOIN_MAINNET_RPC_PORT
    node_set.lnd.node_port = LND_DEFAULT_PEER_PORT
    node_set.lnd.grpc_port = LND_DEFAULT_GRPC_PORT
    node_set.lnd.rest_port = LND_DEFAULT_REST_PORT
    node_set.bitcoin.zmq_block_port = 18500
    node_set.bitcoin.zmq_tx_port = 18501
    node_set.bitcoin.zmq_tx_port = 18501
    ports_layout = PortsLayout(node_set)
    return ports_layout


class TestPortsLayout(object):
    def test_bitcoin_network_port(self,
                                  ports_layout: PortsLayout,
                                  qtbot: QTest):
        assert ports_layout.bitcoin_network_port.text().endswith(
            str(BITCOIN_MAINNET_PEER_PORT)
        )

    def test_lnd_network_port(self,
                              ports_layout: PortsLayout,
                              qtbot: QTest):
        assert ports_layout.lnd_network_port.text().endswith(
            str(LND_DEFAULT_PEER_PORT)
        )

    def test_zmq_ports(self,
                       ports_layout: PortsLayout,
                       qtbot: QTest):
        assert ports_layout.zmq_ports.text().endswith('18500/18501')

    def test_rpc_port(self,
                       ports_layout: PortsLayout,
                       qtbot: QTest):
        assert ports_layout.rpc_port.text().endswith(
            str(BITCOIN_MAINNET_RPC_PORT)
        )

    def test_grpc_port(self,
                      ports_layout: PortsLayout,
                      qtbot: QTest):
        assert ports_layout.grpc_port.text().endswith(
            str(LND_DEFAULT_GRPC_PORT)
        )

    def test_rest_port(self,
                       ports_layout: PortsLayout,
                       qtbot: QTest):
        assert ports_layout.rest_port.text().endswith(
            str(LND_DEFAULT_REST_PORT)
        )
