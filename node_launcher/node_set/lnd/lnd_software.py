from node_launcher.constants import TARGET_LND_RELEASE, OPERATING_SYSTEM
from node_launcher.node_set.lib.software import Software


class LndSoftware(Software):
    def __init__(self):
        super().__init__(
            software_name='lnd',
            release_version=TARGET_LND_RELEASE
        )
        self.github_team = 'lightningnetwork'
        self.download_name = f'lnd-{OPERATING_SYSTEM}-amd64-{self.release_version}'
        self.download_url = f'https://github.com' \
            f'/{self.github_team}' \
            f'/{self.software_name}' \
            f'/releases' \
            f'/download' \
            f'/{self.release_version}' \
            f'/{self.download_destination_file_name}'

    @property
    def daemon(self):
        return self.lnd

    @property
    def lnd(self) -> str:
        return self.executable_path('lnd')

    @property
    def lncli(self) -> str:
        return self.executable_path('lncli')

    @property
    def downloaded_bin_path(self):
        return self.version_path
