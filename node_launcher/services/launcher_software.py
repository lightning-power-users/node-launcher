from node_launcher.services.node_software import NodeSoftware


class LauncherSoftware(NodeSoftware):
    def __init__(self):
        super().__init__()
        self.github_team = 'pierrerochard'
        self.github_repo = 'node-launcher'

