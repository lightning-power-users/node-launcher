import pytest

from node_launcher.constants import NODE_LAUNCHER_RELEASE
from node_launcher.services.launcher_software import LauncherSoftware


@pytest.fixture
def launcher_software() -> LauncherSoftware:
    launcher_software = LauncherSoftware()

    return launcher_software


class TestLauncherSoftware(object):
    def test_get_latest_release_version(self, launcher_software: LauncherSoftware):
        assert launcher_software.get_latest_release_version() == NODE_LAUNCHER_RELEASE
