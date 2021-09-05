import pytest

from node_launcher.system_keyring import SystemKeyring


@pytest.fixture
def system_keyring():
    ring = SystemKeyring()
    return ring


class TestSystemKeyring(object):
    def test_system_keyring(self, system_keyring: SystemKeyring):
        assert system_keyring.backend.name

    def test_get_password(self, system_keyring: SystemKeyring):
        system_keyring.set_password('node_launcher_testing',
                                    'node_launcher_tester',
                                    'node_launcher_test_password')
        password = system_keyring.get_password(
            'node_launcher_testing',
            'node_launcher_tester'
        )
        assert password == 'node_launcher_test_password'
        system_keyring.delete_password('node_launcher_testing',
                                       'node_launcher_tester')
