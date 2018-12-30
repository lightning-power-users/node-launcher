import os
from tempfile import TemporaryDirectory

import pytest

from node_launcher.constants import TARGET_LND_RELEASE
from node_launcher.services.lnd_software import LndSoftware


def mock_get_latest_release_version(*args):
    return TARGET_LND_RELEASE


@pytest.fixture
def lnd_software():
    with TemporaryDirectory() as tmpdirname:
        lnd_software = LndSoftware(tmpdirname)
        lnd_software.get_latest_release_version = mock_get_latest_release_version
        return lnd_software


class TestLndSoftware(object):
    @pytest.mark.slow
    def test_lnd(self, lnd_software: LndSoftware):
        assert os.path.isfile(lnd_software.lnd)

    @pytest.mark.slow
    def test_lncli(self, lnd_software: LndSoftware):
        assert os.path.isfile(lnd_software.lncli)

    def test_release_version(self, lnd_software: LndSoftware):
        assert lnd_software.release_version == TARGET_LND_RELEASE

    @pytest.mark.slow
    def test_get_latest_release_version(self):
        latest = LndSoftware().get_latest_release_version()
        if latest is not None:
            assert latest == TARGET_LND_RELEASE

    def test_binary_name(self, lnd_software: LndSoftware):
        name = lnd_software.download_name
        assert len(name)

    def test_binary_compressed_name(self, lnd_software: LndSoftware):
        name = lnd_software.download_compressed_name
        assert len(name)

    def test_binaries_directory(self, lnd_software: LndSoftware):
        d = lnd_software.downloads_directory_path
        assert os.path.isdir(d)

    def test_binary_directory(self, lnd_software: LndSoftware):
        d = lnd_software.binary_directory_path
        assert os.path.isdir(d)

    def test_download_url(self, lnd_software: LndSoftware):
        url = lnd_software.download_url
        assert len(url)

    @pytest.mark.slow
    def test_download(self, lnd_software: LndSoftware):
        lnd_software.download()
        assert os.path.isfile(lnd_software.download_compressed_path)

