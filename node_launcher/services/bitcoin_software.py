import os

from node_launcher.constants import (
    IS_LINUX,
    IS_MACOS,
    IS_WINDOWS,
    OPERATING_SYSTEM,
    TARGET_BITCOIN_RELEASE
)
from node_launcher.services.node_software import NodeSoftwareABC


class BitcoinSoftware(NodeSoftwareABC):

    def __init__(self, override_directory: str = None):
        super().__init__(override_directory)
        self.release_version = TARGET_BITCOIN_RELEASE.replace('v', '')
        self.github_team = 'bitcoin'
        self.github_repo = 'bitcoin'

    @property
    def bitcoin_qt(self) -> str:
        return self.executable_path('bitcoin-qt')

    @property
    def bitcoin_cli(self) -> str:
        return self.executable_path('bitcoin-cli')

    @property
    def bitcoind(self) -> str:
        return self.executable_path('bitcoind')

    @property
    def uncompressed_directory_name(self) -> str:
        if IS_LINUX:
            name = '-'.join(self.download_name.split('-')[0:2])
        else:
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
        elif IS_MACOS:
            os_name = 'osx64'
        elif IS_LINUX:
            os_name = 'x86_64-linux-gnu'
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
