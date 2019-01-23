import time
import urllib
import subprocess
import zipfile
import os
import os.path
from os.path import expanduser
from urllib.request import urlopen
from typing import Optional, List

from node_launcher.constants import BITCOIN_DATA_PATH, BITCOIN_CONF_PATH, TOR_DATA_PATH, \
    TOR_TORRC_PATH, LND_CONF_PATH , TOR_PATH, TOR_EXE_PATH, OPERATING_SYSTEM, IS_WINDOWS, \
    IS_MACOS

class SetupTor(object):
    def __init__(self, node_set):
        self.node_set = node_set

    def edit_bitcoin_conf(self):
        self.node_set.bitcoin.file['proxy'] = '127.0.0.1:9050'
        self.node_set.bitcoin.file['listen'] = True
        self.node_set.bitcoin.file['bind'] = '127.0.0.1'
        self.node_set.bitcoin.file['debug'] ='tor'

    def edit_lnd_conf(self):
        self.node_set.lnd.file['listen'] = 'localhost'
        self.node_set.lnd.file['tor.active'] = True
        self.node_set.lnd.file['tor.v3'] = True
        self.node_set.lnd.file['tor.streamisolation'] = True

    def downloadtor(self):
        if IS_WINDOWS:
            url = 'https://www.torproject.org/dist/torbrowser/8.0.4/tor-win32-0.3.4.9.zip'
            f = urllib.request.urlopen(url)
            file = f.read()
            f.close()
            f2 = open('tor-win32-0.3.4.9.zip', 'wb')
            f2.write(file)
            f2.close()
        elif IS_MACOS:
            url = 'https://www.torproject.org/dist/torbrowser/8.0.4/TorBrowser-8.0.4-osx64_en-US.dmg'
            urllib.request.urlretrieve(url, expanduser('~/Downloads/TorBrowser-8.0.4-osx64_en-US.dmg'))

    def installtor(self):
        if IS_WINDOWS:
            torpath = str(TOR_PATH[OPERATING_SYSTEM])
            if not os.path.exists(torpath):
                os.makedirs(torpath)
            zip_ref = zipfile.ZipFile(r'tor-win32-0.3.4.9.zip', 'r')
            zip_ref.extractall(torpath)
            zip_ref.close()
        elif IS_MACOS:
            bash_torpath = expanduser('~/Library/Application\ Support/Tor/')
            torpath = expanduser('~/Library/Application Support/Tor/')
            if not os.path.exists(torpath):
                os.makedirs(torpath)
            bashcommand_attach = 'hdiutil attach ~/Downloads/TorBrowser-8.0.4-osx64_en-US.dmg'
            bashcommand_detach = 'hdiutil detach /Volumes/Tor\ Browser'
            cp = ["cp -R /Volumes/Tor\ Browser/Tor\ Browser.app ", str(bash_torpath)]
            bashcommand_cp =  ""
            bashcommand_cp = bashcommand_cp.join(cp)
            subprocess.run(['bash', '-c', bashcommand_attach])
            subprocess.run(['bash', '-c', bashcommand_cp])
            subprocess.run(['bash', '-c', bashcommand_detach])

    def runtor(self):
        if IS_WINDOWS:
            subprocess.Popen(str(TOR_EXE_PATH[OPERATING_SYSTEM]))
        elif IS_MACOS:
            subprocess.Popen(expanduser('~/Library/Application Support/Tor/Tor Browser.app/Contents/MacOS/Tor/tor.real'))


    def write_torrc(self):
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

    def launch(self):
        self.edit_bitcoin_conf()
        self.edit_lnd_conf()
        self.downloadtor()
        self.installtor()
        self.write_torrc()
        self.runtor()
