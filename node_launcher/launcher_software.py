from node_launcher.node_set.lib.software import Software


class LauncherSoftware(Software):
    def __init__(self):
        super().__init__()
        self.github_team = 'pierrerochard'
        self.github_repo = 'node-launcher'

