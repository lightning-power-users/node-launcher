from dataclasses import dataclass, field
import os

from node_launcher.constants import (
    BITCOIND,
    IS_LINUX,
    IS_WINDOWS,
    NODE_LAUNCHER_DATA_PATH,
    NodeSoftwareName,
    OperatingSystem)
from node_launcher.node_set.lib.constants import SOFTWARE_METADATA
from node_launcher.node_set.lib.os_metadata import OsMetadata


@dataclass
class SoftwareMetadata:
    node_software_name: NodeSoftwareName
    operating_system: OperatingSystem
    github_team: str = field(init=False)
    download_url: str = field(init=False)
    cli_name: str = field(init=False)
    os_metadata: OsMetadata = field(init=False)

    def __post_init__(self):
        self.os_metadata = OsMetadata(
            operating_system=self.operating_system,
            node_software_name=self.node_software_name
        )
        self.download_url = '/'.join([
            SOFTWARE_METADATA[self.node_software_name]['release_url'],
            self.download_destination_file_name
        ])

        if self.node_software_name == 'lnd':
            self.downloaded_bin_path = self.version_path
        else:
            self.downloaded_bin_path = os.path.join(self.version_path, 'bin')
        self.cli_name = SOFTWARE_METADATA[self.node_software_name]['cli_name']

    @property
    def launcher_data_path(self) -> str:
        data = NODE_LAUNCHER_DATA_PATH[self.operating_system]
        return data

    @property
    def software_directory(self) -> str:
        path = os.path.join(self.launcher_data_path, str(self.node_software_name))
        return path

    @property
    def download_destination_file_name(self) -> str:
        return self.os_metadata.download_name + self.os_metadata.compressed_suffix

    @property
    def download_destination_file_path(self) -> str:
        return os.path.join(self.software_directory,
                            self.download_destination_file_name)

    @property
    def version_path(self) -> str:
        path = os.path.join(self.software_directory,
                            self.uncompressed_directory_name)
        return path


    @property
    def static_bin_path(self) -> str:
        path = os.path.join(self.launcher_data_path, 'bin')
        return path

    def executable_path(self, name):
        if IS_WINDOWS:
            name += '.exe'
        latest_executable = os.path.join(self.static_bin_path, name)
        return latest_executable

    @property
    def uncompressed_directory_name(self) -> str:
        if self.node_software_name == BITCOIND:
            if IS_LINUX:
                name = '-'.join(self.os_metadata.download_name.split('-')[0:2])
            else:
                name = '-'.join(self.os_metadata.download_name.split('-')[:-1])
                if name == 'bitcoin-0.19.0.1':
                    return name
                elif name.count('.') == 3:
                    name = '.'.join(name.split('.')[:-1])
            return name

        return self.os_metadata.download_name
