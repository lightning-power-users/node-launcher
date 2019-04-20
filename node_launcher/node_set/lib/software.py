import os
import subprocess
import tarfile
import zipfile

import requests
from PySide2.QtCore import QThreadPool, QObject, Signal

from node_launcher.constants import (
    NODE_LAUNCHER_DATA_PATH,
    OPERATING_SYSTEM,
    IS_WINDOWS
)
from node_launcher.gui.components.thread_worker import Worker
from node_launcher.logging import log
from .constants import (
    DEFAULT_COMPRESSED_SUFFIX,
    DEFAULT_WINDOWS_COMPRESSED_SUFFIX
)
from .node_status import SoftwareStatus


class Software(QObject):
    current_status: SoftwareStatus
    software_name: str
    github_team: str

    status = Signal(str)

    def __init__(self):
        super().__init__()
        self.compressed_suffix = DEFAULT_COMPRESSED_SUFFIX
        if IS_WINDOWS:
            self.compressed_suffix = DEFAULT_WINDOWS_COMPRESSED_SUFFIX

    def change_status(self, new_status: SoftwareStatus):
        self.current_status = new_status
        self.status.emit(new_status)

    def update(self):
        self.change_status(SoftwareStatus.CHECKING_DOWNLOAD)
        if os.path.isfile(self.download_destination_file_path):
            self.change_status(SoftwareStatus.SOFTWARE_READY)
        else:
            self.change_status(SoftwareStatus.DOWNLOADING_SOFTWARE)
            worker = Worker(self.download,
                            source_url=self.download_url,
                            destination=self.download_destination_file_path)
            worker.signals.finished.connect(
                lambda: self.change_status(SoftwareStatus.SOFTWARE_DOWNLOADED)
            )
            worker.signals.result.connect(self.install)
            QThreadPool().start(worker)

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
                progress = int((downloaded / total_length) * 100)
                log.debug('Download progress', progress=progress)
                progress_callback.emit(progress)

    def install(self):
        # Todo: move to a thread so it doesn't block the GUI
        log.debug('Installing software')
        self.change_status(SoftwareStatus.INSTALLING_SOFTWARE)
        self.extract(
            source=self.download_destination_file_path,
            destination=self.download_destination_directory
        )
        self.link_static_bin(
            source_directory=self.downloaded_bin_path,
            destination_directory=self.static_bin_path
        )
        self.change_status(SoftwareStatus.SOFTWARE_INSTALLED)
        self.change_status(SoftwareStatus.SOFTWARE_READY)

    def extract(self, source, destination):
        log.debug('Extracting downloaded software',
                  source=source,
                  destination=destination)
        if self.compressed_suffix == '.zip':
            with zipfile.ZipFile(source) as zip_file:
                zip_file.extractall(path=destination)
        elif 'tar' in self.compressed_suffix:
            with tarfile.open(source) as tar:
                tar.extractall(path=destination)
        elif self.compressed_suffix == '.dmg':
            log.debug('Attaching disk image', source=source)
            subprocess.run(
                [
                    f'hdiutil attach {source}'
                ], shell=True)
            app_source_path = '/Volumes/Tor Browser/Tor Browser.app'
            log.debug('Copying app from disk image',
                      app_source_path=app_source_path,
                      destination=destination)
            subprocess.run(
                [
                    f'cp -R {app_source_path} {destination}'
                ], shell=True)
            disk_image_path = '/Volumes/Tor Browser'
            log.debug('Detaching disk image', disk_image_path=disk_image_path)
            subprocess.run([
                f'hdiutil detach {disk_image_path}'
            ], shell=True)

    @staticmethod
    def link_static_bin(source_directory, destination_directory):
        log.debug(
            'Linking from downloaded bin directory to static bin directory',
            source_directory=source_directory,
            destination_directory=destination_directory
        )
        os.makedirs(destination_directory)
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
    def download_destination_directory(self) -> str:
        path = os.path.join(self.launcher_data_path, self.software_name)
        return path

    @property
    def download_destination_file_name(self) -> str:
        return self.download_name + self.compressed_suffix

    @property
    def download_destination_file_path(self) -> str:
        return os.path.join(self.download_destination_directory,
                            self.download_destination_file_name)

    @property
    def binary_directory_path(self) -> str:
        path = os.path.join(self.download_destination_directory,
                            self.download_name)
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
