import time
import urllib
import subprocess
import zipfile
import os.path
from urllib.request import urlopen

from node_launcher.constants import BITCOIN_DATA_PATH, BITCOIN_CONF_PATH, TOR_DATA_PATH, \
    TOR_TORRC_PATH, LND_CONF_PATH , TOR_PATH, TOR_EXE_PATH, OPERATING_SYSTEM, IS_WINDOWS

class SetupTor(object):
    def __init__(self, node_set):
        self.node_set = node_set

    def edit_bitcoin_conf(self):
        f = open(str(BITCOIN_CONF_PATH[OPERATING_SYSTEM]) , 'a')
        self.node_set.bitcoin.file['proxy'] = '127.0.0.1:9050'
        self.node_set.bitcoin.file['listen'] = '1'
        self.node_set.bitcoin.file['bind'] = '127.0.0.1'
        self.node_set.bitcoin.file['debug'] ='tor'
        f.close()

    def edit_lnd_conf(self):
        f = open(str(LND_CONF_PATH[OPERATING_SYSTEM]), 'a')
        self.node_set.lnd.file['listen'] = 'localhost'
        self.node_set.lnd.file[' ']
        self.node_set.lnd.file['tor.active'] ='1'
        self.node_set.lnd.file['tor.v3'] = '1'
        self.node_set.lnd.file['tor.streamisolation'] ='1'
        f.close()

    def downloadtor(self):
        url = 'https://www.torproject.org/dist/torbrowser/8.0.4/tor-win32-0.3.4.9.zip'
        f = urllib.request.urlopen(url)
        file = f.read()
        f.close()
        f2 = open('tor-win32-0.3.4.9.zip', 'wb')
        f2.write(file)
        f2.close()

    def unziptor(self):
        torpath = str(TOR_PATH[OPERATING_SYSTEM])
        if not os.path.exists(torpath):
            os.makedirs(torpath)
        zip_ref = zipfile.ZipFile(r'tor-win32-0.3.4.9.zip', 'r')
        zip_ref.extractall(torpath)
        zip_ref.close()

    def runtor(self):
        subprocess.Popen(str(TOR_EXE_PATH[OPERATING_SYSTEM]))

    def write_torrc(self):
        tordirpath = str(TOR_DATA_PATH[OPERATING_SYSTEM])
        if not os.path.exists(tordirpath):
            os.makedirs(tordirpath)
        f = open(str(TOR_TORRC_PATH[OPERATING_SYSTEM]), 'a')
        f.write(' \n')
        f.write('ControlPort 9051\n')
        f.write('CookieAuthentication 1\n')
        f.write(' \n')
        f.write('HiddenServiceDir ')
        f.write(os.path.join(tordirpath, 'bitcoin-service'))
        f.write('\n')
        f.write('HiddenServicePort 8333 127.0.0.1:8333\n')
        f.write('HiddenServicePort 18333 127.0.0.1:18333\n')
        f.close()

    def launch(self):
        self.edit_bitcoin_conf()
        self.edit_lnd_conf()
        self.downloadtor()
        self.unziptor()
        self.write_torrc()
        self.runtor()
