from node_launcher.constants import TOR

from node_launcher.node_set.lib.software import Software


class TorSoftware(Software):
    def __init__(self):
        super().__init__(node_software_name=TOR)
