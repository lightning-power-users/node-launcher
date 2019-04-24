from node_launcher.constants import (
    IS_LINUX,
    IS_MACOS,
    IS_WINDOWS,
    OPERATING_SYSTEM,
    TARGET_BITCOIN_RELEASE
)
from node_launcher.node_set.lib.software import Software


class BitcoindSoftware(Software):
    def __init__(self):
        super().__init__(
            software_name='bitcoind',
            release_version=TARGET_BITCOIN_RELEASE
        )
        self.release_version = TARGET_BITCOIN_RELEASE.replace('v', '')
        if IS_WINDOWS:
            os_name = 'win64'
        elif IS_MACOS:
            os_name = 'osx64'
        elif IS_LINUX:
            os_name = 'x86_64-linux-gnu'
        else:
            raise Exception(f'{OPERATING_SYSTEM} is not supported')
        self.download_name = f'bitcoin-{self.release_version}-{os_name}'
        self.download_url = f'https://bitcoincore.org' \
            f'/bin' \
            f'/bitcoin-core-{self.release_version}' \
            f'/{self.download_destination_file_name}'

    @property
    def daemon(self):
        return self.bitcoind

    @property
    def cli(self):
        return self.bitcoin_cli

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
