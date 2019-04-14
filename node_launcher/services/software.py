import os
import tarfile
import zipfile
from abc import ABC, abstractmethod
from typing import Optional

import requests

from node_launcher.constants import NODE_LAUNCHER_DATA_PATH, OPERATING_SYSTEM, IS_WINDOWS


class SoftwareABC(ABC):
    def __init__(self, override_directory: str = None):
        self.override_directory = override_directory
        self.release_version = None
        self.github_team = None
        self.github_repo = None

    @property
    @abstractmethod
    def download_name(self) -> str:
        return ''

    @property
    @abstractmethod
    def download_url(self) -> str:
        return ''

    @property
    @abstractmethod
    def uncompressed_directory_name(self) -> str:
        return ''

    @property
    def download_compressed_name(self) -> str:
        name = self.download_name
        if IS_WINDOWS:
            suffix = '.zip'
        else:
            suffix = '.tar.gz'
        return name + suffix

    @property
    def download_compressed_path(self) -> str:
        return os.path.join(self.downloads_directory_path, self.download_compressed_name)

    @property
    def downloads_directory_path(self) -> str:
        path = os.path.join(self.launcher_data_path, self.github_repo)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    @property
    def binary_directory_path(self) -> str:
        path = os.path.join(self.downloads_directory_path,
                            self.uncompressed_directory_name)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    @property
    @abstractmethod
    def bin_path(self) -> str:
        raise NotImplementedError()

    def executable_path(self, name):
        if IS_WINDOWS:
            name += '.exe'
        executable = os.path.join(self.bin_path, name)
        if not os.path.isfile(executable):
            self.download()
            self.extract()
            self.link_latest_bin()
        latest_executable = os.path.join(self.latest_bin_path, name)
        if not os.path.isfile(latest_executable):
            self.link_latest_bin()
        return latest_executable

    def download(self):
        response = requests.get(self.download_url, stream=True)
        with open(self.download_compressed_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    def extract(self):
        if IS_WINDOWS:
            with zipfile.ZipFile(self.download_compressed_path) as zip_file:
                zip_file.extractall(path=self.downloads_directory_path)
        else:
            with tarfile.open(self.download_compressed_path) as tar:
                tar.extractall(path=self.downloads_directory_path)

    def link_latest_bin(self):
        for executable in os.listdir(self.bin_path):
            source = os.path.join(self.bin_path, executable)
            destination = os.path.join(self.latest_bin_path, executable)
            if os.path.exists(destination):
                os.remove(destination)
            os.link(source, destination)

    @property
    def launcher_data_path(self) -> str:
        if self.override_directory is None:
            data = NODE_LAUNCHER_DATA_PATH[OPERATING_SYSTEM]
        else:
            data = self.override_directory
        if not os.path.exists(data):
            os.mkdir(data)
        return data

    @property
    def latest_bin_path(self) -> str:
        path = os.path.join(self.launcher_data_path, 'bin')
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def get_latest_release_version(self) -> Optional[str]:
        github_url = 'https://api.github.com'
        releases_url = github_url + f'/repos/{self.github_team}/{self.github_repo}/releases'
        try:
            response = requests.get(releases_url)
        except requests.exceptions.RequestException:
            return None
        if response.status_code != 200:
            return None
        release = response.json()[0]
        return release['tag_name']


class Software(SoftwareABC):

    @property
    def uncompressed_directory_name(self) -> str:
        return ''

    @property
    def bin_path(self) -> str:
        return ''

    @property
    def download_name(self) -> str:
        return ''

    @property
    def download_compressed_name(self) -> str:
        return ''

    @property
    def download_compressed_path(self) -> str:
        return ''

    @property
    def downloads_directory_path(self) -> str:
        return ''

    @property
    def binary_directory_path(self) -> str:
        return ''

    @property
    def download_url(self) -> str:
        return ''

    def download(self):
        pass

    def extract(self):
        pass
