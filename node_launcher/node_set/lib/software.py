import os
import shutil
import stat
import subprocess
import tarfile
from zipfile import ZipFile, BadZipFile

import requests
from node_launcher.gui.qt import QThreadPool, QObject, Signal

from node_launcher.constants import NodeSoftwareName, OperatingSystem
from node_launcher.gui.components.thread_worker import Worker
from node_launcher.app_logging import log
from node_launcher.node_set.lib.software_metadata import SoftwareMetadata
from .node_status import SoftwareStatus


class Software(QObject):
    node_software_name: NodeSoftwareName
    metadata: SoftwareMetadata
    current_status: SoftwareStatus

    status = Signal(str)
    download_progress = Signal(str)

    def __init__(self, operating_system: OperatingSystem,
                 node_software_name: NodeSoftwareName):
        super().__init__()
        self.node_software_name = node_software_name
        self.metadata = SoftwareMetadata(node_software_name, operating_system=operating_system)
        self.threadpool = QThreadPool()

    def update_status(self, new_status: SoftwareStatus):
        log.debug(f'update_status {self.node_software_name} software',
                  new_status=new_status)
        self.current_status = new_status
        self.status.emit(str(new_status))

    @property
    def daemon(self):
        latest_executable = self.metadata.executable_path(
            self.metadata.os_metadata.daemon_name
        )
        return latest_executable

    @property
    def cli(self):
        latest_executable = self.metadata.executable_path(
            self.metadata.cli_name
        )
        return latest_executable

    def update(self):
        self.update_status(SoftwareStatus.CHECKING_DOWNLOAD)
        is_downloaded = os.path.isfile(self.metadata.download_destination_file_path)
        is_installed = os.path.isdir(self.metadata.version_path)
        if is_downloaded and is_installed:
            self.link_static_bin(
                source_directory=self.metadata.downloaded_bin_path,
                destination_directory=self.metadata.static_bin_path
            )
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
            source_url=self.metadata.download_url,
            destination_directory=self.metadata.software_directory,
            destination_file=self.metadata.download_destination_file_name
        )
        worker.signals.progress.connect(self.emit_download_progress)
        worker.signals.result.connect(
            lambda: self.update_status(SoftwareStatus.SOFTWARE_DOWNLOADED)
        )
        worker.signals.result.connect(self.install)
        self.threadpool.start(worker)

    def emit_download_progress(self, percent):
        msg = f'{percent}% finished downloading {self.node_software_name} software'
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
            source=self.metadata.download_destination_file_path,
            destination=self.metadata.software_directory
        )
        self.link_static_bin(
            source_directory=self.metadata.downloaded_bin_path,
            destination_directory=self.metadata.static_bin_path
        )
        self.update_status(SoftwareStatus.SOFTWARE_INSTALLED)
        self.update_status(SoftwareStatus.SOFTWARE_READY)

    def extract(self, source: str, destination: str):
        os.makedirs(destination, exist_ok=True)
        log.debug('Extracting downloaded software',
                  source=source,
                  destination=destination)
        if self.metadata.os_metadata.compressed_suffix == '.zip':
            try:
                with ZipFile(source) as zip_file:
                    if self.node_software_name != 'tor':
                        zip_file.extractall(path=destination)
                    else:
                        os.makedirs(self.metadata.downloaded_bin_path, exist_ok=True)
                        for file in zip_file.filelist:
                            if file.filename.endswith('dll') or file.filename.endswith('exe'):
                                destination_exe = os.path.join(self.metadata.downloaded_bin_path, file.filename.split('/')[-1])
                                with zip_file.open(file.filename) as zf, open(destination_exe, 'wb') as f:
                                    shutil.copyfileobj(zf, f)
            except BadZipFile:
                log.debug('BadZipFile', destination=destination, exc_info=True)
                os.remove(source)
                self.update()

        elif 'tar' in self.metadata.os_metadata.compressed_suffix:
            with tarfile.open(source) as tar:
                if self.node_software_name != 'tor':
                    tar.extractall(path=destination)
                else:
                    os.makedirs(self.metadata.downloaded_bin_path, exist_ok=True)
                    tor_files = [
                        'libcrypto.so.1.0.0',
                        'libevent-2.1.so.6',
                        'libssl.so.1.0.0',
                        'tor'
                    ]
                    for tor_file in tor_files:
                        file_name = 'tor-browser_en-US/Browser/TorBrowser/Tor/' + tor_file
                        destination_file = os.path.join(self.metadata.downloaded_bin_path, tor_file)
                        extracted_file = tar.extractfile(file_name)
                        with open(destination_file, 'wb') as f:
                            shutil.copyfileobj(extracted_file, f)
                            if tor_file == 'tor':
                                st = os.stat(destination_file)
                                os.chmod(destination_file, st.st_mode | stat.S_IEXEC)

        elif self.metadata.os_metadata.compressed_suffix == '.dmg':
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
                'MacOS', 'Tor'
            )
            file_names = [
                'tor.real',
                'libevent-2.1.7.dylib'
            ]
            os.makedirs(self.metadata.downloaded_bin_path, exist_ok=True)
            for file_name in file_names:
                log.debug('Copying app from disk image',
                          app_source_path=app_source_path,
                          destination=self.metadata.downloaded_bin_path)
                source_path = os.path.join(app_source_path, file_name)
                shutil.copy(src=source_path, dst=self.metadata.downloaded_bin_path)

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
