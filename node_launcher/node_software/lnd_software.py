import os
import tarfile
import zipfile

import requests

from node_launcher.constants import TARGET_LND_RELEASE, OPERATING_SYSTEM, WINDOWS
from node_launcher.node_software.node_software import NodeSoftwareABC


class LndSoftware(NodeSoftwareABC):
    def __init__(self, override_directory: str = None):
        super().__init__(override_directory)
        self.release_version = self.get_latest_release_version()

    @property
    def lnd(self) -> str:
        lnd = os.path.join(self.binary_directory, 'lnd')
        if OPERATING_SYSTEM == WINDOWS:
            lnd += '.exe'
        if not os.path.isfile(lnd):
            self.download()
            self.extract()
        return lnd

    @property
    def release_version(self) -> str:
        return self.__release_version

    @release_version.setter
    def release_version(self, value):
        self.__release_version = value

    @staticmethod
    def get_latest_release_version() -> str:
        github_url = 'https://api.github.com'
        lnd_url = github_url + '/repos/lightningnetwork/lnd/releases'
        response = requests.get(lnd_url)
        if response.status_code == 403:
            return TARGET_LND_RELEASE
        release = response.json()[0]
        return release['tag_name']

    @property
    def binary_name(self) -> str:
        return f'lnd-{OPERATING_SYSTEM}-amd64-{self.release_version}'

    @property
    def binary_compressed_name(self) -> str:
        name = self.binary_name
        if OPERATING_SYSTEM == WINDOWS:
            suffix = '.zip'
        else:
            suffix = '.tar.gz'
        return name + suffix

    @property
    def binary_compressed_path(self) -> str:
        return os.path.join(self.binaries_directory, self.binary_compressed_name)

    @property
    def binaries_directory(self) -> str:
        path = os.path.join(self.launcher_data_path, 'lnd')
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    @property
    def binary_directory(self) -> str:
        path = os.path.join(self.binaries_directory,
                            self.binary_name)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    @property
    def download_url(self) -> str:
        lnd_url = 'https://github.com/lightningnetwork/lnd/'
        dl_url = ''.join([
            lnd_url,
            'releases/download/',
            f'{self.release_version}/',
            self.binary_compressed_name
        ])
        return dl_url

    def download(self):
        response = requests.get(self.download_url, stream=True)
        with open(self.binary_compressed_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    def extract(self):
        if OPERATING_SYSTEM == WINDOWS:
            with zipfile.ZipFile(self.binary_compressed_path) as zip_file:
                zip_file.extractall(path=self.binaries_directory)
        else:
            with tarfile.open(self.binary_compressed_path) as tar:
                tar.extractall(path=self.binaries_directory)
