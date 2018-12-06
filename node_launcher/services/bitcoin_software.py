import os

from node_launcher.constants import TARGET_BITCOIN_RELEASE, OPERATING_SYSTEM, DARWIN, IS_WINDOWS
from node_launcher.services.node_software import NodeSoftwareABC


class BitcoinSoftware(NodeSoftwareABC):
    release_version = None

    def __init__(self, override_directory: str = None):
        super().__init__(override_directory)
        self.github_team = 'bitcoin'
        self.github_repo = 'bitcoin'
        if self.release_version is None:
            latest = self.get_latest_release_version()
            if latest is None:
                self.release_version = TARGET_BITCOIN_RELEASE
            else:
                self.release_version = latest
        self.release_version = self.release_version.replace('v', '')

    @property
    def bitcoin_qt(self) -> str:
        return self.executable_path('bitcoin-qt')

    @property
    def uncompressed_directory_name(self) -> str:
        name = '-'.join(self.download_name.split('-')[:-1])
        if name.count('.') == 3:
            name = '.'.join(name.split('.')[:-1])
        return name

    @property
    def bin_path(self):
        return os.path.join(self.binary_directory_path, 'bin')

    @property
    def download_name(self) -> str:
        if IS_WINDOWS:
            os_name = 'win64'
        elif OPERATING_SYSTEM == DARWIN:
            os_name = 'osx64'
        else:
            raise Exception(f'{OPERATING_SYSTEM} is not supported')
        return f'bitcoin-{self.release_version}-{os_name}'

    @property
    def download_url(self) -> str:
        download_url = f'https://bitcoincore.org' \
            f'/bin' \
            f'/bitcoin-core-{self.release_version}' \
            f'/{self.download_compressed_name}'
        return download_url
