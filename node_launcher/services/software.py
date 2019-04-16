import os
import tarfile
import zipfile
from typing import Optional

import requests
from PySide2.QtCore import QThreadPool, Signal, QObject

from node_launcher.constants import NODE_LAUNCHER_DATA_PATH, OPERATING_SYSTEM, IS_WINDOWS
from node_launcher.gui.components.thread_worker import Worker


class Software(QObject):
    github_repo: str
    github_team: str

    updating = Signal(bool)
    ready = Signal(bool)

    def __init__(self, override_directory: str = None):
        super().__init__()
        self.override_directory = override_directory

    def run(self):
        if self.needs_update:
            self.updating.emit(True)
            worker = Worker(self.update,
                            download_url=self.download_url,
                            download_compressed_path=self.download_compressed_path,
                            downloads_directory_path=self.downloads_directory_path,
                            bin_path=self.bin_path,
                            latest_bin_path=self.latest_bin_path)
            worker.signals.result.connect(lambda: self.ready.emit(True))
            QThreadPool().start(worker)
        self.ready.emit(True)

    @property
    def download_name(self) -> str:
        raise NotImplementedError()

    @property
    def download_url(self) -> str:
        raise NotImplementedError()

    @property
    def uncompressed_directory_name(self) -> str:
        raise NotImplementedError()

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
    def bin_path(self) -> str:
        raise NotImplementedError()

    def executable_path(self, name):
        if IS_WINDOWS:
            name += '.exe'
        latest_executable = os.path.join(self.latest_bin_path, name)
        return latest_executable

    @staticmethod
    def download(source_url, destination):
        response = requests.get(source_url, stream=True)
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    @classmethod
    def update(cls, download_url, download_compressed_path,
               downloads_directory_path, bin_path, latest_bin_path):
        cls.download(
            source_url=download_url,
            destination=download_compressed_path
        )
        cls.extract(
            source=download_compressed_path,
            destination=downloads_directory_path
        )
        cls.link_latest_bin(
            source_directory=bin_path,
            destination_directory=latest_bin_path
        )

    @staticmethod
    def extract(source, destination):
        if IS_WINDOWS:
            with zipfile.ZipFile(source) as zip_file:
                zip_file.extractall(path=destination)
        else:
            with tarfile.open(source) as tar:
                tar.extractall(path=destination)

    @staticmethod
    def link_latest_bin(source_directory, destination_directory):
        for executable in os.listdir(source_directory):
            source = os.path.join(source_directory, executable)
            destination = os.path.join(destination_directory, executable)
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

    @property
    def needs_update(self) -> bool:
        if self.uncompressed_directory_name not in os.listdir(self.downloads_directory_path):
            return True
        return False
