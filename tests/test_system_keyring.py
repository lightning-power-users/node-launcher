import pytest

from node_launcher.system_keyring import SystemKeyring


@pytest.fixture
def system_keyring():
    ring = SystemKeyring()
    return ring


class TestSystemKeyring(object):
    def test_system_keyring(self, system_keyring: SystemKeyring):
        assert system_keyring.backend.name
