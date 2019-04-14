from node_launcher.constants import TARGET_LND_RELEASE, OPERATING_SYSTEM
from node_launcher.services.software import SoftwareABC


class LndSoftware(SoftwareABC):

    def __init__(self, override_directory: str = None):
        super().__init__(override_directory)
        self.github_team = 'lightningnetwork'
        self.github_repo = 'lnd'
        self.release_version = TARGET_LND_RELEASE

    @property
    def lnd(self) -> str:
        return self.executable_path('lnd')

    @property
    def lncli(self) -> str:
        return self.executable_path('lncli')

    @property
    def download_name(self) -> str:
        return f'lnd-{OPERATING_SYSTEM}-amd64-{self.release_version}'

    @property
    def uncompressed_directory_name(self) -> str:
        return self.download_name

    @property
    def bin_path(self):
        return self.binary_directory_path

    @property
    def download_url(self) -> str:
        download_url = f'https://github.com' \
            f'/{self.github_team}' \
            f'/{self.github_repo}' \
            f'/releases' \
            f'/download' \
            f'/{self.release_version}' \
            f'/{self.download_compressed_name}'
        return download_url
