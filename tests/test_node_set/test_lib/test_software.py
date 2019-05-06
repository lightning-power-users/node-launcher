import os
import shutil
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
    software.test_bin = os.path.join(software.downloaded_bin_path, 'test_bin')
    return software


class DownloadFixture(object):
    def __init__(self, software: Software, tmpdir: str):
        self.tmpdir = tmpdir
        self.software = software
        self.binary_name = 'test_bin'
        self.archive_source = os.path.join(self.tmpdir, 'archive',
                                           self.software.download_name)
        self.bin_path = os.path.join(self.archive_source, 'bin')
        software.bin_path = self.bin_path

    @property
    def binary_path(self):
        os.makedirs(self.bin_path, exist_ok=True)
        return os.path.join(self.bin_path, self.binary_name)

    @property
    def archive_destination_file_path(self):
        return os.path.join(self.tmpdir,
                            self.software.download_destination_file_name)

    def get_content(self):
        file_size = 1024 * 1024
        with open(self.binary_path, 'wb') as f:
            f.write(os.urandom(file_size))

        extension = '.tar.gz'
        format = 'gztar'
        if IS_WINDOWS:
            extension = '.zip'
            format = 'zip'
        make_archive(
            base_name=self.archive_destination_file_path.replace(extension, ''),
            format=format,
            root_dir=os.path.join(self.tmpdir, 'archive')
        )

        content = open(self.archive_destination_file_path, 'rb').read()
        return content


@pytest.mark.software
class TestSoftware(object):
    def test__init__(self, software):
        if IS_WINDOWS:
            assert software.compressed_suffix == DEFAULT_WINDOWS_COMPRESSED_SUFFIX
        else:
            assert software.compressed_suffix == DEFAULT_COMPRESSED_SUFFIX

    def test_update_status(self, software, qtbot):
        with qtbot.waitSignal(software.status, raising=True):
            software.update_status(SoftwareStatus.INSTALLING_SOFTWARE)
        assert software.current_status == str(SoftwareStatus.INSTALLING_SOFTWARE)

    def test_update_download(self, software, qtbot, requests_mock, tmpdir):
        try:
            shutil.rmtree(software.software_directory)
        except FileNotFoundError:
            pass

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
                assert len(requests_mock.request_history) == 1
                assert os.path.isdir(software.software_directory)
                assert os.path.isfile(software.download_destination_file_path)
                assert os.path.isdir(software.version_path)
                assert os.path.isdir(software.bin_path)
                assert os.path.isfile(software.test_bin)

        download_fixture = DownloadFixture(software, tmpdir)
        content = download_fixture.get_content()
        requests_mock.get(software.download_url,
                          content=content,
                          headers={'content-length': str(len(content))})

        software.status.connect(check_file_creation)
        with qtbot.waitSignal(software.status, raising=True,
                              check_params_cb=check_status_order) as blocker:
            software.update()
