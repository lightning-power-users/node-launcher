import time
from unittest.mock import MagicMock

import pytest
from PySide2.QtCore import Qt
from PySide2.QtTest import QTest

from node_launcher.constants import keyring
from node_launcher.gui.main_widget import MainWidget
from node_launcher.node_set.lnd_client.rpc_pb2 import GenSeedResponse


class TestSeedDialog(object):
    @pytest.mark.slow
    def test_show(self, qtbot: QTest, main_widget: MainWidget):
        main_widget.testnet_network_widget.node_set.lnd_client.generate_seed = MagicMock(return_value=GenSeedResponse(cipher_seed_mnemonic=['test', 'seed']))
        qtbot.mouseClick(main_widget.testnet_network_widget.lnd_wallet_layout.create_wallet_button,
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
