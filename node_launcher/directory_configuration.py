import os
import platform
import tarfile

import requests

from node_launcher.constants import DATA_PATH, BITCOIN_QT_PATH


def lnd_release_name(release_tag, operating_system):
    return f'lnd-{operating_system}-amd64-{release_tag}'


def download_url(release_tag: str, operating_system: str = 'darwin'):
    lnd_url = 'https://github.com/lightningnetwork/lnd/'
    dl_url = ''.join([
        lnd_url,
        'releases/download/',
        f'{release_tag}/',
        lnd_release_name(release_tag, operating_system),
        '.tar.gz'
    ])
    return dl_url


def download_and_extract_lnd(data_directory: str,
                             release_tag: str, operating_system: str):
    url = download_url(release_tag, operating_system)
    file_name = url.split('/')[-1]
    destination_file = os.path.join(data_directory, file_name)
    if not os.path.exists(data_directory):
        os.mkdir(data_directory)

    response = requests.get(url, stream=True)
    with open(destination_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    with tarfile.open(destination_file) as tar:
        tar.extractall(path=data_directory)


def get_latest_lnd_release():
    github_url = 'https://api.github.com'
    lnd_url = github_url + '/repos/lightningnetwork/lnd/releases'
    release = requests.get(lnd_url).json()[0]
    return release['tag_name']


class DirectoryConfiguration(object):
    def __init__(self, network: str, pruned: bool,
                 lnd_release_fn=get_latest_lnd_release,
                 lnd_dl_fn=download_and_extract_lnd,
                 override_data=None):
        self.network = network
        self.pruned = pruned
        self.operating_system = platform.system()
        self.lnd_version = lnd_release_fn()
        self.lnd_release_name = lnd_release_name(self.lnd_version,
                                                 self.operating_system)
        self.download_and_extract_lnd = lnd_dl_fn
        self.override_data = override_data

    def data(self) -> str:
        if self.override_data is None:
            data = DATA_PATH[self.operating_system]
        else:
            data = self.override_data

        if not os.path.exists(data):
            os.mkdir(data)

        return data

    def bitcoin_data(self) -> str:
        d = os.path.join(self.data(), 'bitcoin_pruned')
        if not os.path.exists(d):
            os.mkdir(d)
        return d

    def bitcoin_qt(self) -> str:
        return BITCOIN_QT_PATH[self.operating_system]

    def lnd_directory(self):
        d = os.path.join(self.data(), 'lnd')
        if not os.path.exists(d):
            os.mkdir(d)
        return d

    def lnd(self) -> str:
        lnd = os.path.join(self.lnd_directory(), self.lnd_release_name, 'lnd')
        if not os.path.isfile(lnd):
            self.download_and_extract_lnd(self.lnd_directory(),
                                          self.lnd_version,
                                          self.operating_system)
        return lnd

    def lnd_data(self):
        d = os.path.join(self.lnd_directory(), 'data')
        if not os.path.exists(d):
            os.mkdir(d)
        return d
