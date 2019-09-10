from dataclasses import dataclass, field

from node_launcher.constants import OPERATING_SYSTEM, NodeSoftwareName, TOR
from node_launcher.node_set.lib.constants import OS_SOFTWARE_METADATA


@dataclass
class OsMetadata:
    node_software_name: NodeSoftwareName
    compressed_suffix: str = field(init=False)
    download_name: str = field(init=False)
    release_version: str = field(init=False)
    daemon_name: str = field(init=False)

    def __post_init__(self):
        self.compressed_suffix = (
            OS_SOFTWARE_METADATA[self.node_software_name][OPERATING_SYSTEM]
                ['compressed_suffix']
        )
        self.release_version = (
            OS_SOFTWARE_METADATA[self.node_software_name][OPERATING_SYSTEM]
            ['release_version']
        )
        self.download_name = (
            OS_SOFTWARE_METADATA[self.node_software_name][OPERATING_SYSTEM]
            ['download_name']
        ).format(release_version=self.release_version)
        self.daemon_name = (
            OS_SOFTWARE_METADATA[self.node_software_name][OPERATING_SYSTEM]
            ['daemon_name']
        )
