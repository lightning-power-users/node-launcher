import os
import shutil
import stat
import subprocess
import tarfile
from zipfile import ZipFile, BadZipFile

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
    download_progress = Signal(str)

    def __init__(self, software_name: str, release_version: str):
        super().__init__()
        self.software_name = software_name
        self.release_version = release_version
        self.compressed_suffix = DEFAULT_COMPRESSED_SUFFIX
        if IS_WINDOWS:
            self.compressed_suffix = DEFAULT_WINDOWS_COMPRESSED_SUFFIX

    def update_status(self, new_status: SoftwareStatus):
        log.debug(f'update_status {self.software_name} software',
                  new_status=new_status)
        self.current_status = new_status
        self.status.emit(str(new_status))

    def update(self):
        self.update_status(SoftwareStatus.CHECKING_DOWNLOAD)
        is_downloaded = os.path.isfile(self.download_destination_file_path)
        is_installed = os.path.isdir(self.version_path)
        if is_downloaded and is_installed:
            self.update_status(SoftwareStatus.SOFTWARE_READY)
        elif not is_downloaded:
            self.update_status(SoftwareStatus.DOWNLOADING_SOFTWARE)
            self.start_update_worker()
        elif not is_installed:
            self.update_status(SoftwareStatus.SOFTWARE_DOWNLOADED)
            self.install()

    def start_update_worker(self):
        worker = Worker(
            self.download,
            progress_callback=None,
            source_url=self.download_url,
            destination_directory=self.software_directory,
            destination_file=self.download_destination_file_name
        )
        worker.signals.progress.connect(self.emit_download_progress)
        worker.signals.result.connect(
            lambda: self.update_status(SoftwareStatus.SOFTWARE_DOWNLOADED)
        )
        worker.signals.result.connect(self.install)
        QThreadPool().start(worker)

    def emit_download_progress(self, percent):
        msg = f'{percent}% finished downloading {self.software_name} software'
        self.download_progress.emit(msg)

    @staticmethod
    def download(progress_callback, source_url: str,
                 destination_directory: str, destination_file: str):
        log.debug(
            'Downloading',
            source_url=source_url,
            destination_directory=destination_directory,
            destination_file=destination_file
        )
        os.makedirs(destination_directory, exist_ok=True)
        destination = os.path.join(destination_directory, destination_file)

        response = requests.get(source_url, stream=True)
        log.debug('Download response', headers=dict(response.headers))
        if response.status_code != 200:
            log.debug(
                'Download error',
                status_code=response.status_code,
                reason=response.reason
            )
            response.raise_for_status()

        with open(destination, 'wb') as f:
            total_length = float(response.headers['content-length'])
            downloaded = 0.0
            old_progress = 0
            for chunk in response.iter_content(chunk_size=4096):
                downloaded += len(chunk)
                f.write(chunk)
                new_progress = int((downloaded / total_length) * 100)
                if new_progress > old_progress:
                    log.debug('Download progress', progress=new_progress)
                    progress_callback.emit(new_progress)
                    old_progress = new_progress

    def install(self):
        # Todo: move to a thread so it doesn't block the GUI
        self.update_status(SoftwareStatus.INSTALLING_SOFTWARE)
        self.extract(
            source=self.download_destination_file_path,
            destination=self.software_directory
        )
        self.link_static_bin(
            source_directory=self.downloaded_bin_path,
            destination_directory=self.static_bin_path
        )
        self.update_status(SoftwareStatus.SOFTWARE_INSTALLED)
        self.update_status(SoftwareStatus.SOFTWARE_READY)

    def extract(self, source: str, destination: str):
        os.makedirs(destination, exist_ok=True)
        log.debug('Extracting downloaded software',
                  source=source,
                  destination=destination)
        if self.compressed_suffix == '.zip':
            try:
                with ZipFile(source) as zip_file:
                    if self.software_name != 'tor':
                        zip_file.extractall(path=destination)
                    else:
                        os.makedirs(self.downloaded_bin_path, exist_ok=True)
                        for file in zip_file.filelist:
                            if file.filename.endswith('dll') or file.filename.endswith('exe'):
                                destination_exe = os.path.join(self.downloaded_bin_path, file.filename.split('/')[-1])
                                with zip_file.open(file.filename) as zf, open(destination_exe, 'wb') as f:
                                    shutil.copyfileobj(zf, f)
            except BadZipFile:
                log.debug('BadZipFile', destination=destination, exc_info=True)
                os.remove(source)
                self.update()

        elif 'tar' in self.compressed_suffix:
            with tarfile.open(source) as tar:
                if self.software_name != 'tor':
                    tar.extractall(path=destination)
                else:
                    os.makedirs(self.downloaded_bin_path, exist_ok=True)
                    tor_files = [
                        'libcrypto.so.1.0.0',
                        'libevent-2.1.so.6',
                        'libssl.so.1.0.0',
                        'tor'
                    ]
                    for tor_file in tor_files:
                        file_name = 'tor-browser_en-US/Browser/TorBrowser/Tor/' + tor_file
                        destination_file = os.path.join(self.downloaded_bin_path, tor_file)
                        extracted_file = tar.extractfile(file_name)
                        with open(destination_file, 'wb') as f:
                            shutil.copyfileobj(extracted_file, f)
                            if tor_file == 'tor':
                                st = os.stat(destination_file)
                                os.chmod(destination_file, st.st_mode | stat.S_IEXEC)

        elif self.compressed_suffix == '.dmg':
            log.debug('Attaching disk image', source=source)
            escaped_source = source.replace(' ', '\ ')
            result = subprocess.run(
                [
                    f'hdiutil attach {escaped_source}'
                ], shell=True, capture_output=True)
            log.debug('hdiutil attach output',
                      stdout=result.stdout,
                      stderr=result.stderr)
            if result.stderr == b'hdiutil: attach failed - no mountable file systems\n':
                os.remove(source)
                self.update()
                return
            # app_source_path = '/Volumes/Tor Browser/Tor Browser.app'
            app_source_path = os.path.join(
                '/Volumes', 'Tor Browser', 'Tor Browser.app', 'Contents',
                'MacOS', 'Tor', 'tor.real'
            )
            log.debug('Copying app from disk image',
                      app_source_path=app_source_path,
                      destination=self.downloaded_bin_path)
            os.makedirs(self.downloaded_bin_path, exist_ok=True)
            shutil.copy(src=app_source_path, dst=self.downloaded_bin_path)
            disk_image_path = '/Volumes/Tor\ Browser'
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
        os.makedirs(destination_directory, exist_ok=True)
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
    def software_directory(self) -> str:
        path = os.path.join(self.launcher_data_path, self.software_name)
        return path

    @property
    def download_destination_file_name(self) -> str:
        return self.download_name + self.compressed_suffix

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
    def downloaded_bin_path(self) -> str:
        return os.path.join(self.version_path, 'bin')

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
        return self.download_name
