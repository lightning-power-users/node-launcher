import os
from tempfile import TemporaryDirectory

import pytest

from node_launcher.constants import TARGET_BITCOIN_RELEASE, OPERATING_SYSTEM, WINDOWS
from node_launcher.node_set.bitcoind.bitcoin_software import BitcoindSoftware


def mock_get_latest_release_version(*args):
    return TARGET_BITCOIN_RELEASE


@pytest.fixture
def bitcoin_software():
    with TemporaryDirectory() as tmpdirname:
        bitcoin_software = BitcoindSoftware(tmpdirname)
        bitcoin_software.get_latest_release_version = mock_get_latest_release_version
        return bitcoin_software


class TestBitcoinSoftware(object):
    @pytest.mark.slow
    def test_bitcoin_qt(self, bitcoin_software: BitcoindSoftware):
        assert os.path.isfile(bitcoin_software.bitcoin_qt)

    def test_release_version(self, bitcoin_software: BitcoindSoftware):
        assert bitcoin_software.release_version == TARGET_BITCOIN_RELEASE.replace('v', '')

    @pytest.mark.slow
    def test_get_latest_release_version(self):
        latest = BitcoindSoftware().get_latest_release_version()
        if latest is not None:
            assert latest == TARGET_BITCOIN_RELEASE

    def test_binary_name(self, bitcoin_software: BitcoindSoftware):
        assert bitcoin_software.download_name

    def test_binaries_directory(self, bitcoin_software: BitcoindSoftware):
        d = bitcoin_software.software_directory
        assert os.path.isdir(d)

    def test_binary_directory(self, bitcoin_software: BitcoindSoftware):
        d = bitcoin_software.version_path
        assert os.path.isdir(d)

    def test_download_url(self, bitcoin_software: BitcoindSoftware):
        url = bitcoin_software.download_url
        if OPERATING_SYSTEM == WINDOWS:
            assert url == 'https://bitcoincore.org/bin/bitcoin-core-0.17.1/bitcoin-0.17.1-win64.zip'
        assert url

    @pytest.mark.slow
    def test_download(self, bitcoin_software: BitcoindSoftware):
        bitcoin_software.download()
        assert os.path.isfile(bitcoin_software.download_destination_file_path)
