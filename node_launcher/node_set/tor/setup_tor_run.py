from urllib.request import urlopen
from subprocess import call, Popen, PIPE
from tempfile import NamedTemporaryFile
from typing import List, Optional
from os.path import expanduser

from node_launcher.constants import BITCOIN_DATA_PATH, BITCOIN_CONF_PATH, TOR_DATA_PATH, \
    TOR_TORRC_PATH, LND_CONF_PATH , TOR_PATH, TOR_EXE_PATH, OPERATING_SYSTEM, IS_WINDOWS, \
    IS_MACOS, IS_LINUX, LND_DIR_PATH

class SetupTorRun(object):
    
    def __init__(self, node_set):
            self.node_set = node_set

    def run(self):

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
            path= expanduser('~/node-launcher/setup_tor.py')
            command= 'python3 '
            cmd = command + path
            with NamedTemporaryFile(suffix='-tor.command', delete=False) as f:
                f.write(f'#!/bin/sh\n{cmd}\n'.encode('utf-8'))
                f.flush()
                call(['chmod', 'u+x', f.name])
                Popen(['gnome-terminal', '--', f.name], close_fds=True)
