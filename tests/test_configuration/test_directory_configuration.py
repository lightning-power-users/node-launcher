import os
from unittest.mock import MagicMock

import pytest

from node_launcher.configuration.directory_configuration import (
    DirectoryConfiguration
)
from node_launcher.constants import (
    OPERATING_SYSTEM,
    LND_DATA_PATH)


@pytest.fixture
def directory_configuration():
    bitcoin_software = MagicMock()
    lnd_software = MagicMock()
    directory_configuration = DirectoryConfiguration(bitcoin_software=bitcoin_software,
                                                     lnd_software=lnd_software)
    return directory_configuration


class TestDirectoryConfiguration(object):
    def test_lnd_data_path(self, directory_configuration: DirectoryConfiguration):
        assert os.path.isdir(LND_DATA_PATH[OPERATING_SYSTEM])
