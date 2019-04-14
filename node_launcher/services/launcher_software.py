from node_launcher.services.software import Software


class LauncherSoftware(Software):
    def __init__(self):
        super().__init__()
        self.github_team = 'pierrerochard'
        self.github_repo = 'node-launcher'

