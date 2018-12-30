import os

import pytest

from node_launcher.constants import NODE_LAUNCHER_DATA_PATH, OPERATING_SYSTEM
from node_launcher.services.node_software import NodeSoftware


@pytest.fixture
def node_software():
    return NodeSoftware()


class TestNodeSoftware(object):
    def test_launcher_data_path(self, node_software: NodeSoftware):
        assert os.path.isdir(node_software.launcher_data_path)
        assert node_software.launcher_data_path == NODE_LAUNCHER_DATA_PATH[OPERATING_SYSTEM]
