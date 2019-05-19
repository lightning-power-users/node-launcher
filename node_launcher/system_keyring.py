from keyring.backend import KeyringBackend

from node_launcher.constants import IS_WINDOWS, IS_MACOS, IS_LINUX


class SystemKeyring(KeyringBackend):
    backend: KeyringBackend

    def __init__(self):
        if IS_WINDOWS:
            from keyring.backends.Windows import WinVaultKeyring as Keyring
        elif IS_MACOS:
            from keyring.backends.OS_X import Keyring
        elif IS_LINUX:
            from keyring.backends.SecretService import Keyring
        else:
            raise NotImplementedError()

        self.backend = Keyring()

    def set_password(self, service, username, password):
        return self.backend.set_password(service, username, password)

    def get_password(self, service, username):
        return self.backend.get_password(service, username)

    def delete_password(self, service, username):
        return self.backend.delete_password(service, username)
