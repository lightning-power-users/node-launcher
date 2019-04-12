from unittest.mock import MagicMock

import pytest
from PySide2.QtTest import QTest

from node_launcher.constants import (
    LND_DEFAULT_PEER_PORT,
    LND_DEFAULT_GRPC_PORT,
    LND_DEFAULT_REST_PORT
)
from node_launcher.gui.menu.manage_lnd import LndPortsLayout


@pytest.fixture
def lnd_ports_layout() -> LndPortsLayout:
    lnd = MagicMock()
    lnd.node_port = LND_DEFAULT_PEER_PORT
    lnd.grpc_port = LND_DEFAULT_GRPC_PORT
    lnd.rest_port = LND_DEFAULT_REST_PORT
    layout = LndPortsLayout(lnd)
    return layout


class TestLndConfigurationTab(object):
    def test_lnd_network_port(self,
                              lnd_ports_layout,
                              qtbot: QTest):
        assert lnd_ports_layout.lnd_network_port.text().endswith(
            str(LND_DEFAULT_PEER_PORT)
        )

    def test_grpc_port(self,
                       lnd_ports_layout,
                       qtbot: QTest):
        assert lnd_ports_layout.grpc_port.text().endswith(
            str(LND_DEFAULT_GRPC_PORT)
        )

    def test_rest_port(self,
                       lnd_ports_layout,
                       qtbot: QTest):
        assert lnd_ports_layout.rest_port.text().endswith(
            str(LND_DEFAULT_REST_PORT)
        )
