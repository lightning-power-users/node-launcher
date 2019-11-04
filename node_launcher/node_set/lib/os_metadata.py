from dataclasses import dataclass, field

from node_launcher.constants import NodeSoftwareName, OperatingSystem
from node_launcher.node_set.lib.constants import OS_SOFTWARE_METADATA


@dataclass
class OsMetadata:
    node_software_name: NodeSoftwareName
    operating_system: OperatingSystem
    compressed_suffix: str = field(init=False)
    download_name: str = field(init=False)
    release_version: str = field(init=False)
    daemon_name: str = field(init=False)

    def __post_init__(self):
        metadata = OS_SOFTWARE_METADATA[self.node_software_name][self.operating_system]
        self.compressed_suffix = metadata['compressed_suffix']
        self.release_version = metadata['release_version']
        self.download_name = metadata['download_name'].format(
            release_version=self.release_version
        )
        self.daemon_name = metadata['daemon_name']
