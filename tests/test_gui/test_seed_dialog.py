import time
from unittest.mock import MagicMock

import pytest
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest

from node_launcher.constants import keyring
from node_launcher.gui.launch_widget import LaunchWidget
from node_launcher.node_set.lnd_client.rpc_pb2 import GenSeedResponse


class TestSeedDialog(object):

    @pytest.mark.slow
    def test_show(self, qtbot: QTest, launch_widget: LaunchWidget):
        launch_widget.testnet_group_box.node_set.lnd_client.generate_seed = MagicMock(return_value=GenSeedResponse(cipher_seed_mnemonic=['test', 'seed']))
        qtbot.mouseClick(launch_widget.testnet_group_box.lnd_wallet_layout.create_wallet_button,
                         Qt.LeftButton)

    def test_keyring(self):
        timestamp = str(time.time())

        keyring.set_password(service='test_entry',
                             username=timestamp,
                             password='test_password')
        password = keyring.get_password(service='test_entry',
                                        username=timestamp)
        assert password == 'test_password'
        keyring.delete_password(service='test_entry',
                                username=timestamp)
