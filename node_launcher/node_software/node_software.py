import os
from abc import ABC, abstractmethod

from node_launcher.constants import NODE_LAUNCHER_DATA_PATH, OPERATING_SYSTEM


class NodeSoftwareABC(ABC):

    @property
    @abstractmethod
    def release_version(self) -> str:
        return ''

    @staticmethod
    @abstractmethod
    def get_latest_release_version() -> str:
        return ''

    @property
    @abstractmethod
    def binary_name(self) -> str:
        return ''

    @property
    @abstractmethod
    def binaries_directory(self) -> str:
        return ''

    @property
    @abstractmethod
    def binary_directory(self) -> str:
        return ''

    @property
    @abstractmethod
    def download_url(self) -> str:
        return ''

    @abstractmethod
    def download(self):
        return

    @abstractmethod
    def extract(self):
        return

    def __init__(self, override_directory: str = None):
        self.override_directory = override_directory

    @property
    def launcher_data_path(self) -> str:
        if self.override_directory is None:
            data = NODE_LAUNCHER_DATA_PATH[OPERATING_SYSTEM]
        else:
            data = self.override_directory
        if not os.path.exists(data):
            os.mkdir(data)
        return data


class NodeSoftware(NodeSoftwareABC):
    @property
    def release_version(self) -> str:
        return ''

    def get_latest_release_version(self) -> str:
        return ''

    @property
    def binary_name(self) -> str:
        return ''

    @property
    def binaries_directory(self) -> str:
        return ''

    @property
    def binary_directory(self) -> str:
        return ''

    @property
    def download_url(self) -> str:
        return ''

    def download(self):
        pass

    def extract(self):
        pass
