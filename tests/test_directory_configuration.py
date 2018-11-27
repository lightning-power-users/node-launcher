import os
import tempfile
from unittest.mock import MagicMock

import pytest

from node_launcher.constants import (
    TARGET_RELEASE,
    NODE_LAUNCHER_DATA_PATH,
    OPERATING_SYSTEM
)
from node_launcher.configuration.directory_configuration import (
    DirectoryConfiguration
)
from node_launcher.exceptions import BitcoinNotInstalledException


@pytest.fixture
def directory_configuration():
    lnd_release_fn = MagicMock(return_value=TARGET_RELEASE)
    lnd_dl_fn = MagicMock()
    directory_configuration = DirectoryConfiguration(lnd_release_fn=lnd_release_fn,
                                                     lnd_dl_fn=lnd_dl_fn)
    return directory_configuration


# noinspection PyProtectedMember
class TestDirectoryConfiguration(object):
    def test_get_latest_lnd_release(self, directory_configuration):
        assert directory_configuration._get_latest_lnd_release() == TARGET_RELEASE

    def test_data_directory(self, directory_configuration):
        assert os.path.isdir(directory_configuration.data)
        assert directory_configuration.data == NODE_LAUNCHER_DATA_PATH[
            OPERATING_SYSTEM]

    def test_bitcoin_qt(self, directory_configuration):
        try:
            path = directory_configuration.bitcoin_qt
        except BitcoinNotInstalledException:
            return True
        assert os.path.isfile(path)

    def test_lnd(self):
        # This will be slow the first time it is run to download LND
        # and when there are new releases
        directory_configuration = DirectoryConfiguration()
        lnd_executable = directory_configuration.lnd
        print(lnd_executable)
        assert os.path.isfile(lnd_executable)

    @pytest.mark.slow
    def test_download_and_extract_lnd(self, directory_configuration):
        with tempfile.TemporaryDirectory() as tmpdirname:
            directory_configuration.override_data = tmpdirname
            directory_configuration._download_and_extract_lnd()
            assert os.path.isfile(directory_configuration.lnd)
