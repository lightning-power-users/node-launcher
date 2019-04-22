import os
import shutil

import pytest

from node_launcher.node_set.lib.node_status import SoftwareStatus
from node_launcher.node_set.tor.tor_software import TorSoftware


@pytest.fixture
def tor_software():
    tor_software = TorSoftware()
    return tor_software


@pytest.mark.software
class TestTorSoftware(object):
    @pytest.mark.slow
    def test_update(self, tor_software, qtbot):
        shutil.rmtree(tor_software.version_path,
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
                    tor_software.software_directory)
                assert os.path.isfile(
                    tor_software.download_destination_file_path)
                assert os.path.isdir(tor_software.version_path)
                assert os.path.isfile(tor_software.tor)

        tor_software.status.connect(check_file_creation)
        with qtbot.waitSignal(tor_software.status, raising=True,
                              check_params_cb=check_status_order) as blocker:
            tor_software.update()
