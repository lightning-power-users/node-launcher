import os
from shutil import make_archive

import pytest

from node_launcher.constants import IS_WINDOWS
from node_launcher.node_set.lib.constants import (
    DEFAULT_COMPRESSED_SUFFIX,
    DEFAULT_WINDOWS_COMPRESSED_SUFFIX
)
from node_launcher.node_set.lib.node_status import SoftwareStatus
from node_launcher.node_set.lib.software import Software


@pytest.fixture
def software():
    software = Software(software_name='test_software', release_version='0.1.0')
    software.download_name = f'TestSoftware_{software.release_version}'
    software.download_url = 'http://localhost'
    return software


class DownloadFixture(object):
    def __init__(self, software: Software, tmpdir: str):
        self.tmpdir = tmpdir
        self.software = software
        self.binary_name = 'test_bin'
        self.bin_path = os.path.join(self.tmpdir, 'bin')

    @property
    def binary_path(self):
        os.makedirs(self.bin_path, exist_ok=True)
        return os.path.join(self.bin_path, self.binary_name)

    @property
    def archive_path(self):
        return os.path.join(self.tmpdir,
                            self.software.download_destination_file_name)

    def get_content(self):
        file_size = 1024 * 1024
        with open(self.binary_path, 'wb') as f:
            f.write(os.urandom(file_size))

        make_archive(base_name=self.archive_path.replace('.tar.gz', ''),
                     format='gztar',
                     root_dir=self.bin_path)

        content = open(self.archive_path, 'rb').read()
        return content


class TestSoftware(object):
    def test__init__(self, software):
        if IS_WINDOWS:
            assert software.compressed_suffix == DEFAULT_WINDOWS_COMPRESSED_SUFFIX
        else:
            assert software.compressed_suffix == DEFAULT_COMPRESSED_SUFFIX

    def test_change_status(self, software, qtbot):
        with qtbot.waitSignal(software.status, raising=True):
            software.change_status(SoftwareStatus.INSTALLING_SOFTWARE)
        assert software.current_status == SoftwareStatus.INSTALLING_SOFTWARE

    def test_update_ready(self, software, qtbot):
        self.call_count = 0
        expected_status = [
            SoftwareStatus.CHECKING_DOWNLOAD,
            SoftwareStatus.SOFTWARE_READY
        ]

        def signal_cb(new_status):
            correct = new_status == str(expected_status[self.call_count])
            self.call_count += 1
            return correct
        os.makedirs(software.download_destination_directory, exist_ok=True)
        file = open(software.download_destination_file_path, 'w').close()
        with qtbot.waitSignal(software.status, raising=True,
                              check_params_cb=signal_cb) as blocker:
            software.update()

    def test_update_download(self, software, qtbot, requests_mock, tmpdir):
        self.call_count = 0
        expected_status = [
            SoftwareStatus.CHECKING_DOWNLOAD,
            SoftwareStatus.DOWNLOADING_SOFTWARE,
            SoftwareStatus.SOFTWARE_DOWNLOADED,
            SoftwareStatus.INSTALLING_SOFTWARE,
            SoftwareStatus.SOFTWARE_INSTALLED,
            SoftwareStatus.SOFTWARE_READY
        ]

        def signal_cb(new_status):
            correct = new_status == str(expected_status[self.call_count])
            self.call_count += 1
            return correct
        download_fixture = DownloadFixture(software, tmpdir)
        content = download_fixture.get_content()
        requests_mock.get(software.download_url,
                          content=content,
                          headers={'content-length': len(content)})
        if os.path.isfile(software.download_destination_file_path):
            os.remove(software.download_destination_file_path)
        with qtbot.waitSignal(software.status, raising=True,
                              check_params_cb=signal_cb) as blocker:
            software.update()
        assert len(requests_mock.request_history) == 1
