import pytest

from node_launcher.node_set.lib.hard_drives import HardDrives


@pytest.fixture
def hard_drives():
    hard_drives = HardDrives()
    return hard_drives


class TestHardDrives(object):
    def test_get_big_drive(self, hard_drives: HardDrives):
        assert hard_drives.get_big_drive().gb_free > 0
