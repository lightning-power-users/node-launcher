from node_launcher.constants import NODE_LAUNCHER_RELEASE
from node_launcher.services.node_software import NodeSoftware


class LauncherSoftware(NodeSoftware):
    def __init__(self):
        super().__init__()
        self.github_team = 'pierrerochard'
        self.github_repo = 'node-launcher'
        if self.get_latest_release_version() is None:
            self.get_latest_release_version = lambda: NODE_LAUNCHER_RELEASE
