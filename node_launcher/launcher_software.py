from typing import Optional

import requests

from node_launcher.constants import NODE_LAUNCHER_RELEASE
from node_launcher.node_set.lib.software import Software


class LauncherSoftware(Software):
    def __init__(self):
        super().__init__(software_name='node-launcher',
                         release_version=NODE_LAUNCHER_RELEASE)
        self.github_team = 'lightning-power-users'

    def get_latest_release_version(self) -> Optional[str]:
        github_url = 'https://api.github.com'
        releases_url = github_url + f'/repos/{self.github_team}/{self.software_name}/releases'
        try:
            response = requests.get(releases_url)
        except requests.exceptions.RequestException:
            return None
        if response.status_code != 200:
            return None
        release = response.json()[0]
        return release['tag_name']
