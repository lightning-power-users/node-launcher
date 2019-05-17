import os
import shutil

import pytest

from node_launcher.constants import TARGET_BITCOIN_RELEASE, IS_MACOS, IS_WINDOWS
from node_launcher.node_set.lib.node_status import SoftwareStatus
from node_launcher.node_set.bitcoind.bitcoind_software import BitcoindSoftware


@pytest.fixture
def bitcoind_software():
    bitcoind_software = BitcoindSoftware()
    return bitcoind_software


@pytest.mark.software
class TestBitcoindSoftware(object):
    @pytest.mark.slow
    def test_update(self, bitcoind_software, qtbot):
        shutil.rmtree(bitcoind_software.version_path,
                      ignore_errors=True)
        self.call_count = 0
        expected_status = [
            SoftwareStatus.CHECKING_DOWNLOAD,
            SoftwareStatus.DOWNLOADING_SOFTWARE,
            SoftwareStatus.SOFTWARE_DOWNLOADED,
            SoftwareStatus.INSTALLING_SOFTWARE,
            SoftwareStatus.SOFTWARE_INSTALLED,
            SoftwareStatus.SOFTWARE_READY
        ]

        def check_status_order(new_status):
            correct = new_status == str(expected_status[self.call_count])
            self.call_count += 1
            return correct

        def check_file_creation(new_status):
            if new_status == str(SoftwareStatus.SOFTWARE_READY):
                assert os.path.isdir(bitcoind_software.software_directory)
                assert os.path.isfile(
                    bitcoind_software.download_destination_file_path)
                assert os.path.isdir(bitcoind_software.version_path)
                assert os.path.isfile(bitcoind_software.bitcoind)

        bitcoind_software.status.connect(check_file_creation)
        with qtbot.waitSignal(bitcoind_software.status, raising=True,
                              check_params_cb=check_status_order) as blocker:
            bitcoind_software.update()

    def test_bitcoin_qt(self, bitcoind_software: BitcoindSoftware):
        assert os.path.isfile(bitcoind_software.bitcoin_qt)

    def test_bitcoin_cli(self, bitcoind_software: BitcoindSoftware):
        assert os.path.isfile(bitcoind_software.bitcoin_cli)

    def test_bitcoind(self, bitcoind_software: BitcoindSoftware):
        assert os.path.isfile(bitcoind_software.bitcoind)

    def test_release_version(self, bitcoind_software: BitcoindSoftware):
        assert bitcoind_software.release_version == TARGET_BITCOIN_RELEASE.replace('v', '')

    def test_binary_name(self, bitcoind_software: BitcoindSoftware):
        assert bitcoind_software.download_name

    def test_binaries_directory(self, bitcoind_software: BitcoindSoftware):
        d = bitcoind_software.software_directory
        assert os.path.isdir(d)

    def test_binary_directory(self, bitcoind_software: BitcoindSoftware):
        d = bitcoind_software.version_path
        assert os.path.isdir(d)

    def test_download_url(self, bitcoind_software: BitcoindSoftware):
        url = bitcoind_software.download_url
        if IS_WINDOWS:
            assert url == 'https://bitcoincore.org/bin/bitcoin-core-0.18.0/bitcoin-0.18.0-win64.zip'
        elif IS_MACOS:
            assert url == 'https://bitcoincore.org/bin/bitcoin-core-0.18.0/bitcoin-0.18.0-osx64.tar.gz'
        assert url
