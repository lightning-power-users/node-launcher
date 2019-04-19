import getpass
import zipfile
import os
import subprocess

from node_launcher.constants import (
    TOR_PATH,
    OPERATING_SYSTEM,
    IS_WINDOWS,
    IS_MACOS,
    IS_LINUX,
    TARGET_WINDOWS_TOR_VERSION,
    TARGET_TOR_RELEASE
)
from node_launcher.logging import log
from node_launcher.node_set.lib.software import Software


class TorSoftware(Software):
    release_version = TARGET_TOR_RELEASE
    windows_version = TARGET_WINDOWS_TOR_VERSION
    software_name = 'tor'

    def __init__(self):
        super().__init__()
        if IS_MACOS:
            self.compressed_suffix = '.dmg'

    @property
    def tor(self) -> str:
        if IS_MACOS or IS_LINUX:
            name = 'tor.real'
        elif IS_WINDOWS:
            name = 'tor.exe'
        else:
            raise NotImplementedError()
        latest_executable = os.path.join(self.static_bin_path, name)
        return latest_executable

    @property
    def download_name(self) -> str:
        if IS_MACOS:
            return f'TorBrowser-{self.release_version}-osx64_en-US'
        elif IS_WINDOWS:
            return f'tor-win64-{self.windows_version}'

    @property
    def download_url(self) -> str:
        return f'http://www.torproject.org/dist/torbrowser/' \
            f'{self.release_version}/{self.download_destination_file_name}'

    @property
    def uncompressed_directory_name(self) -> str:
        return self.download_name

    @property
    def bin_path(self):
        if IS_MACOS:
            return os.path.join(self.binary_directory_path,
                                'Tor Browser.app', 'Contents',
                                'MacOS', 'Tor')
        elif IS_WINDOWS:
            return os.path.join(self.binary_directory_path, 'Tor')
        return

    @staticmethod
    def extract(source, destination):
        if IS_WINDOWS:
            with zipfile.ZipFile(source) as zip_file:
                zip_file.extractall(path=destination)
        elif IS_MACOS:
            # TODO see if this below is covered by `torpath` variable
            tor_path = str(TOR_PATH[OPERATING_SYSTEM])
            if not os.path.exists(tor_path):
                os.makedirs(tor_path)

            bash_command_attach = f'hdiutil attach {source}'
            subprocess.run(['bash', '-c', bash_command_attach])

            bash_command_cp = f'cp -R /Volumes/Tor Browser/Tor Browser.app {destination}'
            subprocess.run(['bash', '-c', bash_command_cp])

            bash_command_detach = 'hdiutil detach /Volumes/Tor Browser'
            subprocess.run(['bash', '-c', bash_command_detach])

    @staticmethod
    def deb_install():
        def deb_permissions():
            log.debug('Updating user permissions')
            bash_command_chmod = 'sudo chmod a+rw /etc/apt/sources.list'
            subprocess.run(['bash', '-c', bash_command_chmod])

        def deb_install_tor():
            if IS_LINUX:
                import platform
                dist = platform.dist()
                dist = list(dist)
                codename = dist[2]
                deba = 'deb http://deb.torproject.org/torproject.org ', str(codename), ' main\n'
                deb_line = ''
                deb_line = deb_line.join(deba)
                debb = 'deb-src http://deb.torproject.org/torproject.org ', str(codename), ' main'
                deb_src = ''
                deb_src = deb_src.join(debb)
                f = open('/etc/apt/sources.list', 'a')
                f.write(deb_line)
                f.write(str(deb_src))
                f.close()
                log.debug('Installing Tor.....')
                bash_command_gpg_key = 'gpg --keyserver keys.gnupg.net --recv 886DDD89'
                bash_command_gpg_export = 'gpg --export A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89 | sudo apt-key add -'
                bash_command_update = 'sudo apt-get update'
                bash_command_install_tor = 'sudo apt-get install tor deb.torproject.org-keyring'
                subprocess.run(['bash', '-c', bash_command_gpg_key])
                subprocess.run(['bash', '-c', bash_command_gpg_export])
                subprocess.run(['bash', '-c', bash_command_update])
                subprocess.run(['bash', '-c', bash_command_install_tor])

        def deb_modify_user():
            for line in open('/usr/share/tor/tor-service-defaults-torrc'):
                if 'User' in line:
                    newline = line.replace('User ', '''''')
                    newline = str(newline.rstrip())
                    tor_user = str(newline)
                continue
            username = str(getpass.getuser())
            bash_command_modify = 'sudo usermod -a -G ', str(tor_user), ' ', str(username)
            bash_command_usermod = ''
            bash_command_usermod = bash_command_usermod.join(bash_command_modify)
            subprocess.run(['bash', '-c', bash_command_usermod])
            log.debug('Tor setup is complete!')
            input('Press enter to exit...')

        if IS_LINUX:
            deb_permissions()
            deb_install_tor()
            deb_modify_user()
