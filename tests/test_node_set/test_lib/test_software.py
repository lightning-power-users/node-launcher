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
    software = Software()
    return software


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

