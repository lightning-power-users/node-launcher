import os
import tempfile
from unittest.mock import MagicMock

import pytest

from node_launcher.constants import TARGET_RELEASE, DATA_PATH, OPERATING_SYSTEM
from node_launcher.directory_configuration import (
    DirectoryConfiguration,
    get_latest_lnd_release,
    download_and_extract_lnd
)


@pytest.fixture
def directory_configuration():
    lnd_release_fn = MagicMock(return_value=TARGET_RELEASE)
    lnd_dl_fn = MagicMock()
    directory_configuration = DirectoryConfiguration('testnet', pruned=True,
                                                     lnd_release_fn=lnd_release_fn,
                                                     lnd_dl_fn=lnd_dl_fn)
    return directory_configuration


@pytest.fixture
def test_get_latest_lnd_release():
    assert get_latest_lnd_release() == TARGET_RELEASE


@pytest.mark.slow
def test_download_and_extract_lnd(directory_configuration: DirectoryConfiguration):
    with tempfile.TemporaryDirectory() as tmpdirname:
        directory_configuration.override_data = tmpdirname
        download_and_extract_lnd(directory_configuration.lnd_directory(),
                                 directory_configuration.lnd_version)
        assert os.path.isfile(directory_configuration.lnd())


class TestDirectoryConfiguration(object):
    def test_data_directory(self, directory_configuration):
        assert os.path.isdir(directory_configuration.data())
        assert directory_configuration.data() == DATA_PATH[OPERATING_SYSTEM]

    def test_bitcoin_qt(self, directory_configuration):
        assert os.path.isfile(directory_configuration.bitcoin_qt())

    def test_lnd(self):
        # This will be slow the first time it is run to download LND
        # and when there are new releases
        directory_configuration = DirectoryConfiguration('testnet', pruned=True)
        lnd_executable = directory_configuration.lnd()
        print(lnd_executable)
        assert os.path.isfile(lnd_executable)
