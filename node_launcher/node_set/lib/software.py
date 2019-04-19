import os
import tarfile
import zipfile
from typing import Optional

import requests
from PySide2.QtCore import QThreadPool, Signal, QObject

from node_launcher.constants import NODE_LAUNCHER_DATA_PATH, OPERATING_SYSTEM, \
    IS_WINDOWS
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
        self.status.emit(NodeStatus.CHECKING_DOWNLOAD)
        if not os.path.isfile(self.download_destination_file_path):
            self.status.emit(NodeStatus.DOWNLOADING_SOFTWARE)
            worker = Worker(self.download,
                            source_url=self.download_url,
                            destination=self.download_destination_file_path)
            worker.signals.finished.connect(
                lambda: self.status.emit(NodeStatus.SOFTWARE_DOWNLOADED)
            )
            worker.signals.result.connect(self.install)
            QThreadPool().start(worker)
        else:
            self.status.emit(NodeStatus.SOFTWARE_READY)

    @property
    def launcher_data_path(self) -> str:
        data = NODE_LAUNCHER_DATA_PATH[OPERATING_SYSTEM]
        return data

    @property
    def download_destination_directory(self) -> str:
        path = os.path.join(self.launcher_data_path, self.github_repo)
        return path

    @property
    def download_destination_file_name(self) -> str:
        name = self.download_name
        if IS_WINDOWS:
            suffix = '.zip'
        else:
            suffix = '.tar.gz'
        return name + suffix

    @property
    def download_destination_file_path(self) -> str:
        return os.path.join(self.download_destination_directory,
                            self.download_destination_file_name)

    @property
    def binary_directory_path(self) -> str:
        path = os.path.join(self.download_destination_directory,
                            self.uncompressed_directory_name)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def executable_path(self, name):
        if IS_WINDOWS:
            name += '.exe'
        latest_executable = os.path.join(self.latest_bin_path, name)
        return latest_executable

    @staticmethod
    def download(progress_callback, source_url: str,
                 destination_directory: str, destination_file: str):
        log.debug(
            'Downloading',
            source_url=source_url,
            destination_directory=destination_directory,
            destination_file=destination_file
        )
        os.makedirs(destination_directory)
        destination = os.path.join(destination_directory, destination_file)
        with open(destination, 'wb') as f:
            response = requests.get(source_url, stream=True)
            log.debug('Download response', headers=dict(response.headers))
            total_length = float(response.headers['content-length'])
            downloaded = 0.0
            for chunk in response.iter_content(chunk_size=4096):
                downloaded += len(chunk)
                f.write(chunk)
                progress = int((downloaded/total_length)*100)
                log.debug('Download progress', progress=progress)
                progress_callback.emit(progress)

    def install(self):
        log.debug('Installing software')
        self.status.emit(NodeStatus.INSTALLING_SOFTWARE)
        self.extract(
            source=self.download_destination_file_path,
            destination=self.download_destination_directory
        )
        self.link_latest_bin(
            source_directory=self.bin_path,
            destination_directory=self.latest_bin_path
        )
        self.status.emit(NodeStatus.SOFTWARE_INSTALLED)
        self.status.emit(NodeStatus.SOFTWARE_READY)

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
        if self.uncompressed_directory_name not in os.listdir(
                self.download_destination_directory):
            log.debug(f'{self.uncompressed_directory_name} needs update')
            return True
        log.debug(f'{self.uncompressed_directory_name} is ready')
        return False
