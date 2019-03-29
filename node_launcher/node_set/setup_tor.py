import time
import urllib
import getpass
import zipfile
import os

from os.path import expanduser
from urllib.request import urlopen, urlretrieve
from tempfile import NamedTemporaryFile
from typing import List, Optional

from node_launcher.constants import TOR_PATH, \
    TOR_EXE_PATH, OPERATING_SYSTEM, IS_WINDOWS, \
    IS_MACOS, IS_LINUX


# FIXME
import subprocess
from subprocess import call, Popen, PIPE

    
def downloadtor():
    print('Downloading Tor...')
    if IS_WINDOWS:
        url = 'http://www.torproject.org/dist/torbrowser/8.0.6/tor-win32-0.3.5.7.zip'
        f = urllib.request.urlopen(url)
        file = f.read()
        f.close()
        f2 = open('tor-win32-0.3.5.7.zip', 'wb')
        f2.write(file)
        f2.close()
    elif IS_MACOS:
        url = 'https://www.torproject.org/dist/torbrowser/8.0.6/TorBrowser-8.0.6-osx64_en-US.dmg'
        urllib.request.urlopen(url)

def deb_install():

    def deb_permissions():
        
        print('Updating user permissions')
        bashcommand_chmod = 'sudo chmod a+rw /etc/apt/sources.list'
        subprocess.run(['bash', '-c', bashcommand_chmod])

    def deb_install_tor():
        if IS_LINUX:
            import platform
            dist = platform.dist()
            dist = list(dist)
            codename = dist[2]
            deba = 'deb http://deb.torproject.org/torproject.org ', str(codename),' main\n'
            deb_line = ""
            deb_line = deb_line.join(deba)
            debb = 'deb-src http://deb.torproject.org/torproject.org ', str(codename), ' main'
            deb_src = ""
            deb_src = deb_src.join(debb)
            f = open('/etc/apt/sources.list', 'a')
            f.write(deb_line)
            f.write(str(deb_src))
            f.close()
            print('Installing Tor.....')
            bashcommand_gpg_key = 'gpg --keyserver keys.gnupg.net --recv 886DDD89'
            bashcommand_gpg_export = 'gpg --export A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89 | sudo apt-key add -'
            bashcommand_update = 'sudo apt-get update'
            bashcommand_install_tor = 'sudo apt-get install tor deb.torproject.org-keyring'
            subprocess.run(['bash', '-c', bashcommand_gpg_key])
            subprocess.run(['bash', '-c', bashcommand_gpg_export])
            subprocess.run(['bash', '-c', bashcommand_update])
            subprocess.run(['bash', '-c', bashcommand_install_tor])

    def deb_modify_user():
        for line in open("/usr/share/tor/tor-service-defaults-torrc"):
            if "User" in line:
                newline = line.replace("User ", "")
                newline = str(newline.rstrip())
                tor_user = str(newline)
            continue
        username = str(getpass.getuser())
        bashcommand_modify = 'sudo usermod -a -G ', str(tor_user), ' ', str(username)
        bashcommand_usermod = ""
        bashcommand_usermod = bashcommand_usermod.join(bashcommand_modify)
        subprocess.run(['bash', '-c', bashcommand_usermod])
        print('Tor setup is complete!')
        input("Press enter to exit...")      

    if IS_LINUX:
        deb_permissions()
        deb_install_tor()
        deb_modify_user()

def installtor():
    torpath = str(TOR_PATH[OPERATING_SYSTEM])
    if IS_WINDOWS:
        print('Installing Tor...')
        if not os.path.exists(torpath):
            os.makedirs(torpath)
        zip_ref = zipfile.ZipFile(r'tor-win32-0.3.5.7.zip', 'r')
        zip_ref.extractall(torpath)
        zip_ref.close()
    elif IS_MACOS:
        print('Installing Tor...')
        # TODO see if this below is covered by `torpath` variable
        bash_torpath = expanduser('~/Library/Application\ Support/Tor/')
        if not os.path.exists(torpath):
            os.makedirs(torpath)
        bashcommand_attach = 'hdiutil attach ~/Downloads/TorBrowser-8.0.6-osx64_en-US.dmg'
        bashcommand_detach = 'hdiutil detach /Volumes/Tor\ Browser'
        cp = ["cp -R /Volumes/Tor\ Browser/Tor\ Browser.app ", str(bash_torpath)]
        bashcommand_cp =  ""
        bashcommand_cp = bashcommand_cp.join(cp)
        subprocess.run(['bash', '-c', bashcommand_attach])
        subprocess.run(['bash', '-c', bashcommand_cp])
        subprocess.run(['bash', '-c', bashcommand_detach])

def runtor():
    print('Launching Tor...')    
    path= TOR_EXE_PATH[OPERATING_SYSTEM]
    cmd = path
    if IS_MACOS:
        with NamedTemporaryFile(suffix='-run_tor.command', delete=False) as f:
            f.write(f'#!/bin/sh\n{cmd}\n'.encode('utf-8'))
            f.flush()
            call(['chmod', 'u+x', f.name])
            result = Popen(['open', '-W', f.name], close_fds=True)
        time.sleep(2)
        print('Tor setup is complete!')
    elif IS_WINDOWS:
        from subprocess import DETACHED_PROCESS, CREATE_NEW_PROCESS_GROUP
        with NamedTemporaryFile(suffix='-run_tor.bat', delete=False) as f:
            f.write(cmd.encode('utf-8'))
            f.flush()
            result = Popen(
                ['start', 'powershell', '-noexit', '-Command', f.name],
                stdin=PIPE, stdout=PIPE, stderr=PIPE,
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                close_fds=True, shell=True)
        time.sleep(2)
        print('Tor setup is complete!')
        input("Press enter to exit...")



def run_tor(self):

    if IS_MACOS:
        path= expanduser('~/node-launcher/node_launcher/node_set/setup_tor.py')
        command = expanduser('~/node-launcher/venv/bin/python ')
        cmd = command + path
        with NamedTemporaryFile(suffix='-tor.command', delete=False) as f:
            f.write(f'#!/bin/sh\n{cmd}\n'.encode('utf-8'))
            f.flush()
            call(['chmod', 'u+x', f.name])
            result = Popen(['open', '-W', f.name], close_fds=True)
    elif IS_WINDOWS:
        path= expanduser('~\node-launcher\setup_tor.py')
        command= 'python3 '
        cmd = command + path
        from subprocess import DETACHED_PROCESS, CREATE_NEW_PROCESS_GROUP
        with NamedTemporaryFile(suffix='-tor.bat', delete=False) as f:
            f.write(cmd.encode('utf-8'))
            f.flush()
            result = Popen(
                ['start', 'powershell', '-noexit', '-Command', f.name],
                stdin=PIPE, stdout=PIPE, stderr=PIPE,
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                close_fds=True, shell=True)
    elif IS_LINUX:
        path= expanduser('~/node-launcher/node_launcher/node_set/setup_tor.py')
        command= 'python3 '
        cmd = command + path
        with NamedTemporaryFile(suffix='-tor.command', delete=False) as f:
            f.write(f'#!/bin/sh\n{cmd}\n'.encode('utf-8'))
            f.flush()
            call(['chmod', 'u+x', f.name])
            Popen(['gnome-terminal', '--', f.name], close_fds=True)


def launch():
    if IS_MACOS or IS_WINDOWS:
        downloadtor()
        installtor()
        runtor()

    elif IS_LINUX:
        deb_install()


if __name__ == '__main__':
    launch()
