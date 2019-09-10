from node_launcher.constants import BITCOIND, IS_LINUX
from node_launcher.node_set.lib.software import Software


class BitcoindSoftware(Software):
    def __init__(self):
        super().__init__(node_software_name=BITCOIND)

    @property
    def uncompressed_directory_name(self) -> str:
        if IS_LINUX:
            name = '-'.join(self.download_name.split('-')[0:2])
        else:
            name = '-'.join(self.download_name.split('-')[:-1])
            if name.count('.') == 3:
                name = '.'.join(name.split('.')[:-1])
        return name
