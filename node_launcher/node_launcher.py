import os
from subprocess import Popen, call, PIPE
from tempfile import NamedTemporaryFile
from typing import List

from node_launcher.constants import DARWIN, WINDOWS, OPERATING_SYSTEM


class BitcoinNotInstalledException(Exception):
    pass


def launch(command: List[str]):
    if not os.path.isfile(command[0]):
        raise BitcoinNotInstalledException()

    if OPERATING_SYSTEM == WINDOWS:
        from subprocess import DETACHED_PROCESS, CREATE_NEW_PROCESS_GROUP
        command[0] = '"' + command[0] + '"'
        cmd = ' '.join(command)
        with NamedTemporaryFile(suffix='-btc.bat', delete=False) as f:
            f.write(cmd.encode('utf-8'))
            f.flush()
            result = Popen(['start', 'powershell', '-noexit', '-windowstyle', 'hidden', '-Command', f.name],
                           stdin=PIPE, stdout=PIPE, stderr=PIPE,
                           creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                           close_fds=True, shell=True)
    else:
        result = Popen(command, close_fds=True, shell=False)

    return result


def launch_terminal(command: List[str]):
    command[0] = '"' + command[0] + '"'
    cmd = ' '.join(command)
    if OPERATING_SYSTEM == DARWIN:
        with NamedTemporaryFile(suffix='-lnd.command', delete=False) as f:
            f.write(f'#!/bin/sh\n{cmd}\n'.encode('utf-8'))
            f.flush()
            call(['chmod', 'u+x', f.name])
            Popen(['open', '-W', f.name], close_fds=True)
    elif OPERATING_SYSTEM == WINDOWS:
        from subprocess import DETACHED_PROCESS, CREATE_NEW_PROCESS_GROUP
        with NamedTemporaryFile(suffix='-lnd.bat', delete=False) as f:
            f.write(cmd.encode('utf-8'))
            f.flush()
            Popen(['start', 'powershell', '-noexit', '-Command', f.name],
                  stdin=PIPE, stdout=PIPE, stderr=PIPE,
                  creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                  close_fds=True, shell=True)


class NodeLauncher(object):
    def __init__(self, command_generator, launch_fn=launch,
                 launch_terminal_fn=launch_terminal):
        self.command_generator = command_generator
        self.launch = launch_fn
        self.launch_terminal = launch_terminal_fn

    def testnet_bitcoin_qt_node(self):
        result = self.launch(self.command_generator.testnet_bitcoin_qt())
        return result

    def mainnet_bitcoin_qt_node(self):
        result = self.launch(self.command_generator.mainnet_bitcoin_qt())
        return result

    def testnet_lnd_node(self):
        result = self.launch_terminal(self.command_generator.testnet_lnd())
        return result

    def mainnet_lnd_node(self):
        result = self.launch_terminal(self.command_generator.mainnet_lnd())
        return result
