import platform
import subprocess
from tempfile import NamedTemporaryFile
from typing import List


def launch(command: List[str]):
    result = subprocess.Popen(command, close_fds=True)
    return result


def launch_terminal(command: List[str]):
    command[0] = '"' + command[0] + '"'
    cmd = ' '.join(command)
    operating_system = platform.system()
    if operating_system == 'Darwin':
        with NamedTemporaryFile(suffix='-lnd.command', delete=False) as f:
            f.write(f'#!/bin/sh\n{cmd}\n'.encode('utf-8'))
            f.flush()
            subprocess.call(['chmod', 'u+x', f.name])
            subprocess.Popen(['open', '-W', f.name], close_fds=True)


class NodeLauncher(object):
    def __init__(self, command_generator, launch_fn=launch,
                 launch_terminal_fn=launch_terminal):
        self.command_generator = command_generator
        self.launch = launch_fn
        self.launch_terminal = launch_terminal_fn

    def launchTestnetBitcoinQtNode(self):
        result = self.launch(self.command_generator.testnet_bitcoin_qt())
        return result

    def launchMainnetBitcoinQtNode(self):
        result = self.launch(self.command_generator.mainnet_bitcoin_qt())
        return result

    def launchTestnetLndNode(self):
        result = self.launch_terminal(self.command_generator.testnet_lnd())
        return result

    def launchMainnetLndNode(self):
        result = self.launch_terminal(self.command_generator.mainnet_lnd())
        return result
