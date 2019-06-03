from node_launcher.constants import TARGET_NODEJS_RELEASE, NODEJS_WEBSITE, \
    IS_MACOS, IS_LINUX, IS_WINDOWS
from node_launcher.node_set.lib.software import Software


class NodejsSoftware(Software):
    def __init__(self):
        super().__init__(
            software_name='nodejs',
            release_version=TARGET_NODEJS_RELEASE
        )
        if IS_MACOS:
            self.download_name = f'node-{self.release_version}-darwin-x64'
        elif IS_LINUX:
            self.download_name = f'node-{self.release_version}-linux-x64'
        elif IS_WINDOWS:
            self.download_name = f'node-{self.release_version}-win-x64'
        self.download_url = f'{NODEJS_WEBSITE}{self.release_version}/{self.download_destination_file_name}'

    @property
    def npm(self) -> str:
        return self.executable_path('npm')
