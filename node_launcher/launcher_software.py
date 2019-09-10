from typing import Optional

import requests

from node_launcher.constants import NODE_LAUNCHER


class LauncherSoftware(object):
    @staticmethod
    def get_latest_release_version() -> Optional[str]:
        github_url = 'https://api.github.com'
        releases_url = github_url + f'/repos/lightning-power-users/{NODE_LAUNCHER}/releases'
        try:
            response = requests.get(releases_url)
        except requests.exceptions.RequestException:
            return None
        if response.status_code != 200:
            return None
        release = response.json()[0]
        return release['tag_name']
