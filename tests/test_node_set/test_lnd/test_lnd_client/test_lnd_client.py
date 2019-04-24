from unittest.mock import MagicMock

import pytest

from node_launcher.node_set.lnd.lnd_client import LndClient


@pytest.fixture
def mocked_lnd_client() -> LndClient:
    lnd_client = LndClient()
    lnd_client._wallet_unlocker = MagicMock()
    lnd_client._lnd_client = MagicMock()
    return lnd_client


class TestLndClient(object):
    def test_wallet_unlocker(self,):
        assert LndClient().wallet_unlocker

    def test_generate_seed(self, mocked_lnd_client: LndClient):
        mocked_lnd_client.generate_seed()
        assert mocked_lnd_client.wallet_unlocker.called_once()

    def test_initialize_wallet(self, mocked_lnd_client: LndClient):
        mocked_lnd_client.initialize_wallet(
            wallet_password='test_password',
            seed=['test', 'mnemonic']
        )
        assert mocked_lnd_client.wallet_unlocker.called_once()

    def test_unlock(self, mocked_lnd_client: LndClient):
        mocked_lnd_client.unlock('test_password')
        assert mocked_lnd_client.wallet_unlocker.called_once()
