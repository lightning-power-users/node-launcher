from unittest.mock import MagicMock

import pytest
from PySide2.QtTest import QTest

from node_launcher.constants import (
    BITCOIN_MAINNET_PEER_PORT,
    BITCOIN_MAINNET_RPC_PORT,
    TARGET_BITCOIN_RELEASE
)
from node_launcher.gui.menu.manage_bitcoind import BitcoindPortsLayout


@pytest.fixture
def bitcoind_ports_layout() -> BitcoindPortsLayout:
    bitcoin = MagicMock()
    bitcoin.node_port = BITCOIN_MAINNET_PEER_PORT
    bitcoin.rpc_port = BITCOIN_MAINNET_RPC_PORT
    bitcoin.zmq_block_port = 18500
    bitcoin.zmq_tx_port = 18501
    bitcoin.zmq_tx_port = 18501
    bitcoin.software.release_version = TARGET_BITCOIN_RELEASE
    layout = BitcoindPortsLayout(bitcoin)
    return layout


class TestBitcoindConfigurationTab(object):
    def test_bitcoin_network_port(self,
                                  bitcoind_ports_layout,
                                  qtbot: QTest):
        assert bitcoind_ports_layout.bitcoin_network_port.text().endswith(
            str(BITCOIN_MAINNET_PEER_PORT)
        )

    def test_rpc_port(self,
                      bitcoind_ports_layout,
                      qtbot: QTest):
        assert bitcoind_ports_layout.rpc_port.text().endswith(
            str(BITCOIN_MAINNET_RPC_PORT)
        )

    def test_zmq_ports(self,
                       bitcoind_ports_layout,
                       qtbot: QTest):
        assert bitcoind_ports_layout.zmq_ports.text().endswith('18500/18501')

