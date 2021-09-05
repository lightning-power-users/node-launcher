import os

from node_launcher.constants import (
    IS_WINDOWS,
    IS_MACOS,
    IS_LINUX,
    TARGET_WINDOWS_TOR_VERSION,
    TARGET_TOR_RELEASE,
    TOR_WEBSITE
)
from node_launcher.node_set.lib.software import Software


class TorSoftware(Software):
    def __init__(self):
        super().__init__(
            software_name='tor',
            release_version=TARGET_TOR_RELEASE
        )
        if IS_MACOS:
            self.compressed_suffix = '.dmg'
            self.download_name = f'TorBrowser-{self.release_version}-osx64_en-US'
        elif IS_LINUX:
            self.compressed_suffix = '.tar.xz'
            self.download_name = f'tor-browser-linux64-{self.release_version}_en-US'
        elif IS_WINDOWS:
            self.download_name = f'tor-win64-{TARGET_WINDOWS_TOR_VERSION}'

        self.download_url = f'{TOR_WEBSITE}{self.release_version}/{self.download_destination_file_name}'

    @property
    def daemon(self):
        return self.tor

    @property
    def tor(self) -> str:
        name = 'tor.real'
        if IS_WINDOWS:
            name = 'tor.exe'
        elif IS_LINUX:
            name = 'tor'
        latest_executable = os.path.join(self.static_bin_path, name)
        return latest_executable
