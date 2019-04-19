import os
import tarfile
import zipfile
from typing import Optional

import requests
from PySide2.QtCore import QThreadPool, Signal, QObject

from node_launcher.constants import NODE_LAUNCHER_DATA_PATH, OPERATING_SYSTEM, IS_WINDOWS
from node_launcher.gui.components.thread_worker import Worker
from node_launcher.logging import log
from node_launcher.node_set.lib.node_status import NodeStatus


class Software(QObject):
    github_repo: str
    github_team: str

    status = Signal(str)

    def __init__(self):
        super().__init__()

    def update(self):
        if self.needs_update:
            self.status.emit(NodeStatus.DOWNLOADING_SOFTWARE)
            worker = Worker(self.download,
                            source_url=self.download_url,
                            destination=self.download_compressed_path)
            worker.signals.result.connect(self.install)
            QThreadPool().start(worker)
        self.status.emit(NodeStatus.SOFTWARE_READY)

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
    def download(progress_callback, source_url, destination):
        response = requests.get(source_url, stream=True)
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    def install(self):
        self.status.emit(NodeStatus.INSTALLING_SOFTWARE)
        self.extract(
            source=self.download_compressed_path,
            destination=self.downloads_directory_path
        )
        self.link_latest_bin(
            source_directory=self.bin_path,
            destination_directory=self.latest_bin_path
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
        data = NODE_LAUNCHER_DATA_PATH[OPERATING_SYSTEM]
        return data

    @property
    def latest_bin_path(self) -> str:
        path = os.path.join(self.launcher_data_path, 'bin')
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
        self.status.emit(NodeStatus.CHECKING_SOFTWARE_VERSION)
        if self.uncompressed_directory_name not in os.listdir(self.downloads_directory_path):
            log.debug(f'{self.uncompressed_directory_name} needs update')
            return True
        log.debug(f'{self.uncompressed_directory_name} is ready')
        return False
