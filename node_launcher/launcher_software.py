from typing import Optional

import requests

from node_launcher.node_set.lib.software import Software


class LauncherSoftware(Software):
    def __init__(self):
        super().__init__()
        self.github_team = 'lightning-power-users'
        self.software_name = 'node-launcher'

    def get_latest_release_version(self) -> Optional[str]:
        github_url = 'https://api.github.com'
        releases_url = github_url + f'/repos/{self.github_team}/{self.github_repo}/releases'
        try:
            response = requests.get(releases_url)
        except requests.exceptions.RequestException:
            return None
        if response.status_code != 200:
            return None
        release = response.json()[0]
        return release['tag_name']
