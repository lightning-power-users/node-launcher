import os
import tarfile
import zipfile

import requests

from node_launcher.constants import (
    NODE_LAUNCHER_DATA_PATH,
    BITCOIN_QT_PATH,
    WINDOWS,
    OPERATING_SYSTEM,
    TARGET_RELEASE,
    BITCOIN_DATA_PATH,
    LND_DATA_PATH
)


class DirectoryConfiguration(object):
    def __init__(self,
                 lnd_release_fn=None,
                 lnd_dl_fn=None,
                 override_data=None):

        if lnd_release_fn is None:
            lnd_release_fn = self._get_latest_lnd_release

        if lnd_dl_fn is None:
            lnd_dl_fn = self._download_and_extract_lnd

        self.lnd_release = lnd_release_fn()
        self.lnd_release_name = f'lnd-{OPERATING_SYSTEM}-amd64-{self.lnd_release}'
        self.download_and_extract_lnd = lnd_dl_fn
        self.override_data = override_data
        self.lnd_binaries = os.path.join(self.data(), 'lnd')
        self.lnd_binary_directory = os.path.join(self.lnd_binaries, self.lnd_release_name)

    def data(self) -> str:
        if self.override_data is None:
            data = NODE_LAUNCHER_DATA_PATH[OPERATING_SYSTEM]
        else:
            data = self.override_data

        if not os.path.exists(data):
            os.mkdir(data)

        return data

    @property
    def bitcoin_data_path(self) -> str:
        d = BITCOIN_DATA_PATH[OPERATING_SYSTEM]
        if not os.path.exists(d):
            os.mkdir(d)
        return d

    @property
    def lnd_data_path(self) -> str:
        d = LND_DATA_PATH[OPERATING_SYSTEM]
        if not os.path.exists(d):
            os.mkdir(d)
        return d

    @property
    def bitcoin_qt(self) -> str:
        return BITCOIN_QT_PATH[OPERATING_SYSTEM]

    @property
    def lnd(self) -> str:
        lnd = os.path.join(self.lnd_binaries, self.lnd_release_name, 'lnd')
        if OPERATING_SYSTEM == WINDOWS:
            lnd += '.exe'
        if not os.path.isfile(lnd):
            self.download_and_extract_lnd()
        return lnd

    def download_url(self) -> str:
        lnd_url = 'https://github.com/lightningnetwork/lnd/'

        if OPERATING_SYSTEM == WINDOWS:
            suffix = '.zip'
        else:
            suffix = '.tar.gz'

        dl_url = ''.join([
            lnd_url,
            'releases/download/',
            f'{self.lnd_release}/',
            self.lnd_release_name,
            suffix
        ])
        return dl_url

    def _download_and_extract_lnd(self):

        if not os.path.exists(self.lnd_binary_directory):
            os.mkdir(self.lnd_binary_directory)

        url = self.download_url()

        response = requests.get(url, stream=True)

        file_name = url.split('/')[-1]
        destination_file = os.path.join(self.lnd_binary_directory, file_name)
        with open(destination_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        if OPERATING_SYSTEM == WINDOWS:
            with zipfile.ZipFile(destination_file) as zip_file:
                zip_file.extractall(path=self.lnd_binaries)
        else:
            with tarfile.open(destination_file) as tar:
                tar.extractall(path=self.lnd_binaries)

    @staticmethod
    def _get_latest_lnd_release():
        github_url = 'https://api.github.com'
        lnd_url = github_url + '/repos/lightningnetwork/lnd/releases'
        response = requests.get(lnd_url)
        if response.status_code == 403:
            return TARGET_RELEASE
        release = response.json()[0]
        return release['tag_name']
