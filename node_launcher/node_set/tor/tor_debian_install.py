import subprocess

from node_launcher.constants import IS_LINUX
from node_launcher.logging import log


def deb_install():
    import getpass
    import platform

    def deb_permissions():
        log.debug('Updating user permissions')
        bash_command_chmod = 'sudo chmod a+rw /etc/apt/sources.list'
        subprocess.run(['bash', '-c', bash_command_chmod])

    def deb_install_tor():
        dist = platform.dist()
        dist = list(dist)
        codename = dist[2]
        deba = 'deb http://deb.torproject.org/torproject.org ', str(
            codename), ' main\n'
        deb_line = ''
        deb_line = deb_line.join(deba)
        debb = 'deb-src http://deb.torproject.org/torproject.org ', str(
            codename), ' main'
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
        bash_command_modify = 'sudo usermod -a -G ', str(
            tor_user), ' ', str(username)
        bash_command_usermod = ''
        bash_command_usermod = bash_command_usermod.join(
            bash_command_modify)
        subprocess.run(['bash', '-c', bash_command_usermod])
        log.debug('Tor setup is complete!')
        input('Press enter to exit...')

    if IS_LINUX:
        deb_permissions()
        deb_install_tor()
        deb_modify_user()
