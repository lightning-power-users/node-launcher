import os

import pytest

from node_launcher.constants import OPERATING_SYSTEM, LND
from node_launcher.node_set.lib.constants import TARGET_LND_RELEASE
from node_launcher.node_set.lib.software import Software


@pytest.fixture
def lnd_software():
    lnd_software = Software(operating_system=OPERATING_SYSTEM,
                            node_software_name=LND)
    return lnd_software


class TestLndSoftware(object):
    @pytest.mark.slow
    def test_lnd(self, lnd_software: Software):
        assert os.path.isfile(lnd_software.lnd)

    @pytest.mark.slow
    def test_lncli(self, lnd_software: Software):
        assert os.path.isfile(lnd_software.lncli)

    def test_release_version(self, lnd_software: Software):
        assert lnd_software.release_version == TARGET_LND_RELEASE

    def test_binary_name(self, lnd_software: Software):
        name = lnd_software.download_name
        assert len(name)

    def test_binary_compressed_name(self, lnd_software: Software):
        name = lnd_software.download_destination_file_name
        assert len(name)

    def test_binaries_directory(self, lnd_software: Software):
        d = lnd_software.software_directory
        assert os.path.isdir(d)

    def test_binary_directory(self, lnd_software: Software):
        d = lnd_software.version_path
        assert os.path.isdir(d)

    def test_download_url(self, lnd_software: Software):
        url = lnd_software.download_url
        assert len(url)
