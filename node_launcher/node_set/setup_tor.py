import sys
import time
import urllib
import getpass
import subprocess
import zipfile
import os
import os.path
import time
from os.path import expanduser
from urllib.request import urlopen, urlretrieve
from tempfile import NamedTemporaryFile
from subprocess import call, Popen, PIPE
from typing import List, Optional


from node_launcher.constants import BITCOIN_DATA_PATH, BITCOIN_CONF_PATH, TOR_DATA_PATH, \
    TOR_TORRC_PATH, LND_CONF_PATH , TOR_PATH, TOR_EXE_PATH, OPERATING_SYSTEM, IS_WINDOWS, \
    IS_MACOS, IS_LINUX, LND_DIR_PATH

class SetupTor(object):
    
    def edit_bitcoin_conf():
        print('Node Launcher is preparing your system...')
        time.sleep(2)
        print('NOTE: Restart Bitcoin Core and LND after running this script for changes to take effect')
        time.sleep(2)
        print('Configruing bitcoin.conf...')
        f = open(str(BITCOIN_CONF_PATH[OPERATING_SYSTEM]) , 'a')
        f.write('proxy=127.0.0.1:9050\n')
        f.write('listen=1\n')
        f.write('bind=127.0.0.1\n')
        f.write('debug=tor\n')
        f.close()
        time.sleep(2)

    def edit_lnd_conf():
        print('Configuring lnd.conf...')
        f = open(str(LND_CONF_PATH[OPERATING_SYSTEM]) , 'a')
        f.write(' \n')
        f.write('[Application Options]\n')
        f.write('listen=localhost\n')
        f.write(' \n')
        f.write('[tor]\n')
        f.write('tor.active=1\n')
        f.write('tor.v3=1\n')
        f.write('tor.streamisolation=1\n')
        f.close()
        time.sleep(2)
       
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
        if IS_WINDOWS:
            print('Installing Tor...')
            torpath = str(TOR_PATH[OPERATING_SYSTEM])
            if not os.path.exists(torpath):
                os.makedirs(torpath)
            zip_ref = zipfile.ZipFile(r'tor-win32-0.3.5.7.zip', 'r')
            zip_ref.extractall(torpath)
            zip_ref.close()
        elif IS_MACOS:
            print('Installing Tor...')
            bash_torpath = expanduser('~/Library/Application\ Support/Tor/')
            torpath = expanduser('~/Library/Application Support/Tor/')
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
        if IS_MACOS:
            path= TOR_EXE_PATH[OPERATING_SYSTEM]
            cmd = path
            with NamedTemporaryFile(suffix='-run_tor.command', delete=False) as f:
                f.write(f'#!/bin/sh\n{cmd}\n'.encode('utf-8'))
                f.flush()
                call(['chmod', 'u+x', f.name])
                result = Popen(['open', '-W', f.name], close_fds=True)
            time.sleep(2)
            print('Tor setup is complete!')
        elif IS_WINDOWS:
            path = TOR_EXE_PATH[OPERATING_SYSTEM]
            cmd = path
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


    def write_torrc():
        tordatapath = str(TOR_DATA_PATH[OPERATING_SYSTEM])
        if not os.path.exists(tordatapath):
            os.makedirs(tordatapath)
        f = open(str(TOR_TORRC_PATH[OPERATING_SYSTEM]), 'a')
        f.write(' \n')
        f.write('ControlPort 9051\n')
        f.write('CookieAuthentication 1\n')
        f.write(' \n')
        f.write('HiddenServiceDir ')
        f.write(os.path.join(tordatapath, 'bitcoin-service'))
        f.write('\n')
        f.write('HiddenServicePort 8333 127.0.0.1:8333\n')
        f.write('HiddenServicePort 18333 127.0.0.1:18333\n')
        f.close()

def launch():
    if IS_MACOS or IS_WINDOWS:
        SetupTor.edit_bitcoin_conf()
        SetupTor.edit_lnd_conf()
        SetupTor.downloadtor()
        SetupTor.installtor()
        SetupTor.write_torrc()
        SetupTor.runtor()

    elif IS_LINUX:
        SetupTor.edit_bitcoin_conf()
        SetupTor.deb_install()

launch()