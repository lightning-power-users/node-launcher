import os
from unittest.mock import MagicMock

import pytest

from node_launcher.constants import IS_WINDOWS
from node_launcher.node_set.lnd import (
    Lnd
)
from node_launcher.utilities.utilities import is_port_in_use


class TestDirectoryConfiguration(object):
    def test_lnd_data_path(self, lnd: Lnd):
        assert os.path.isdir(lnd.file['lnddir'])

    def test_multi_property(self, lnd: Lnd):
        lnd.file['multi_property'] = [
            'test1',
            'test2'
        ]
        assert len(lnd.file['multi_property']) == 2

    def test_rest(self, lnd: Lnd):
        assert not is_port_in_use(lnd.rest_port)

    def test_node(self, lnd: Lnd):
        assert not is_port_in_use(lnd.node_port)

    def test_grpc(self, lnd: Lnd):
        assert not is_port_in_use(lnd.grpc_port)

    @pytest.mark.slow
    def test_launch_terminal(self, lnd: Lnd):
        if IS_WINDOWS:
            command = ['set', 'path']
        else:
            command = ['echo', 'hello']
        lnd.lnd = MagicMock(return_value=command)
        result = lnd.launch()
        assert result
