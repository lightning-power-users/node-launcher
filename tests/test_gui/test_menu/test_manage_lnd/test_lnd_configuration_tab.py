from unittest.mock import MagicMock, patch

import pytest
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest

from node_launcher.constants import TARGET_LND_RELEASE
from node_launcher.gui.menu.manage_lnd import LndConfigurationTab


@pytest.fixture
def lnd_configuration_tab() -> LndConfigurationTab:
    lnd = MagicMock()
    lnd.file.directory = '/test/lnd'
    lnd.software.release_version = TARGET_LND_RELEASE
    tab = LndConfigurationTab(lnd)
    return tab


class TestLndConfigurationTab(object):
    @patch('node_launcher.gui.menu.manage_lnd.lnd_configuration_tab.reveal')
    def test_show_lnd_conf(self,
                           reveal_patch: MagicMock,
                           lnd_configuration_tab,
                           qtbot: QTest):
        qtbot.mouseClick(lnd_configuration_tab.show_lnd_conf,
                         Qt.LeftButton)
        reveal_patch.assert_called_with('/test/lnd')

    def test_lnd_version(self,
                         lnd_configuration_tab,
                         qtbot: QTest):
        assert lnd_configuration_tab.lnd_version.text().endswith(
            TARGET_LND_RELEASE
        )
