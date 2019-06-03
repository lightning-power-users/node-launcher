import os
import shutil

import pytest

from node_launcher.constants import TARGET_NODEJS_RELEASE
from node_launcher.node_set.lib.node_status import SoftwareStatus
from node_launcher.node_set.nodejs.nodejs_software import NodejsSoftware


@pytest.fixture
def nodejs_software():
    nodejs_software = NodejsSoftware()
    return nodejs_software


class TestNodejsSoftware(object):
    @pytest.mark.slow
    def test_update(self, nodejs_software: NodejsSoftware, qtbot):
        shutil.rmtree(nodejs_software.version_path,
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
                assert os.path.isdir(
                    nodejs_software.software_directory)
                assert os.path.isfile(
                    nodejs_software.download_destination_file_path)
                assert os.path.isdir(nodejs_software.version_path)
                assert os.path.isfile(nodejs_software.npm)

        nodejs_software.status.connect(check_file_creation)
        with qtbot.waitSignal(nodejs_software.status, raising=True,
                              check_params_cb=check_status_order) as blocker:
            nodejs_software.update()


    def test_release_version(self, nodejs_software: NodejsSoftware):
        assert nodejs_software.release_version == TARGET_NODEJS_RELEASE

    def test_binary_name(self, nodejs_software: NodejsSoftware):
        name = nodejs_software.download_name
        assert len(name)

    def test_binary_compressed_name(self, nodejs_software: NodejsSoftware):
        name = nodejs_software.download_destination_file_name
        assert len(name)

    def test_binaries_directory(self, nodejs_software: NodejsSoftware):
        d = nodejs_software.software_directory
        assert os.path.isdir(d)

    def test_binary_directory(self, nodejs_software: NodejsSoftware):
        d = nodejs_software.version_path
        assert os.path.isdir(d)

    def test_download_url(self, nodejs_software: NodejsSoftware):
        url = nodejs_software.download_url
        assert len(url)
