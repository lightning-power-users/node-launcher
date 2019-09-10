from node_launcher.constants import LND
from node_launcher.node_set.lib.software import Software


class LndSoftware(Software):
    def __init__(self):
        super().__init__(node_software_name=LND)
        self.metadata.downloaded_bin_path = self.metadata.version_path
    
    @property
    def cli(self):
        return self.lncli
    
    @property
    def daemon(self):
        return self.lnd

    @property
    def lnd(self) -> str:
        return self.metadata.executable_path('lnd')

    @property
    def lncli(self) -> str:
        return self.executable_path('lncli')
