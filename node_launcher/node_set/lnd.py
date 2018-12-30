import os
import psutil
import socket
from subprocess import call, Popen, PIPE
from tempfile import NamedTemporaryFile
from typing import List, Optional

from psutil import ZombieProcess, AccessDenied

from node_launcher.node_set.bitcoin import Bitcoin
from node_launcher.services.configuration_file import ConfigurationFile
from node_launcher.constants import LND_DIR_PATH, OPERATING_SYSTEM, IS_WINDOWS, IS_LINUX, IS_MACOS
from node_launcher.services.lnd_software import LndSoftware
from node_launcher.utilities import get_port


class Lnd(object):
    file: ConfigurationFile
    software: LndSoftware
    process: Optional[psutil.Process]

    def __init__(self, network: str, configuration_file_path: str, bitcoin: Bitcoin):
        self.running = False
        self.is_unlocked = False
        self.network = network
        self.bitcoin = bitcoin
        self.file = ConfigurationFile(configuration_file_path)
        self.process = self.find_running_node()
        self.software = LndSoftware()

        self.file['lnddir'] = LND_DIR_PATH[OPERATING_SYSTEM]

        if self.file['debuglevel'] is None:
            self.file['debuglevel'] = 'info'

        self.file['bitcoin.active'] = True
        self.file['bitcoin.node'] = 'bitcoind'
        self.file['bitcoind.rpchost'] = '127.0.0.1'
        self.file['bitcoind.rpcuser'] = self.bitcoin.file['rpcuser']
        self.file['bitcoind.rpcpass'] = self.bitcoin.file['rpcpassword']
        self.file['bitcoind.zmqpubrawblock'] = self.bitcoin.file['zmqpubrawblock']
        self.file['bitcoind.zmqpubrawtx'] = self.bitcoin.file['zmqpubrawtx']

        if self.file['restlisten'] is None:
            self.rest_port = get_port(8080)
            self.file['restlisten'] = f'127.0.0.1:{self.rest_port}'
        else:
            self.rest_port = self.file['restlisten'].split(':')[-1]

        if self.file['listen'] is None:
            self.node_port = get_port(9735)
            self.file['listen'] = f'127.0.0.1:{self.node_port}'
        else:
            self.node_port = self.file['listen'].split(':')[-1]

        if self.file['rpclisten'] is None:
            self.grpc_port = get_port(10009)
            self.file['rpclisten'] = f'0.0.0.0:{self.grpc_port}'
        else:
            self.grpc_port = self.file['rpclisten'].split(':')[-1]

        if self.file['tlsextraip'] is None:
            self.extraip = socket.gethostbyname(socket.gethostname())
            self.file['tlsextraip'] = f'{self.extraip}'
        else:
            self.extraip = self.file['tlsextraip'].split('=')[-1]

    def find_running_node(self) -> Optional[psutil.Process]:
        found_ports = []
        for process in psutil.process_iter():
            try:
                process_name = process.name()
            except ZombieProcess:
                continue
            if 'lnd' in process_name:
                lnd_process = process
                self.is_unlocked = False
                self.running = True
                try:
                    log_file = lnd_process.open_files()[0]
                except IndexError:
                    continue
                if self.network not in log_file.path:
                    continue
                try:
                    for connection in process.connections():
                        found_ports.append((connection.laddr, connection.raddr))
                        if 8080 <= connection.laddr.port <= 9000:
                            self.rest_port = connection.laddr.port
                        elif 10009 <= connection.laddr.port <= 10100:
                            self.grpc_port = connection.laddr.port
                        elif 9735 <= connection.laddr.port < 9800:
                            self.node_port = connection.laddr.port
                            self.is_unlocked = True
                    return lnd_process
                except AccessDenied:
                    continue
        self.running = False
        return None

    @property
    def macaroon_path(self) -> str:
        macaroons_path = os.path.join(self.file['lnddir'], 'data', 'chain',
                                      'bitcoin', self.network)
        return macaroons_path

    @property
    def admin_macaroon_path(self) -> str:
        path = os.path.join(self.macaroon_path, 'admin.macaroon')
        return path

    @property
    def tls_cert_path(self) -> str:
        tls_cert_path = os.path.join(self.file['lnddir'], 'tls.cert')
        return tls_cert_path

    def lnd(self) -> List[str]:
        command = [
            self.software.lnd,
            f'--configfile="{self.file.path}"',
            '--debuglevel=info'
        ]
        if self.network == 'testnet':
            command += [
                '--bitcoin.testnet'
            ]
        else:
            command += [
                '--bitcoin.mainnet'
            ]
        return command

    @property
    def lncli(self) -> List[str]:
        base_command = [
            f'"{self.software.lncli}"',
        ]
        if self.grpc_port != 10009:
            base_command.append(f'--rpcserver=localhost:{self.grpc_port}')
        if self.network != 'mainnet':
            base_command.append(f'--network={self.network}')
        if self.file['lnddir'] != LND_DIR_PATH[OPERATING_SYSTEM]:
            base_command.append(f'''--lnddir="{self.file['lnddir']}"''')
            base_command.append(f'--macaroonpath="{self.macaroon_path}"')
            base_command.append(f'--tlscertpath="{self.tls_cert_path}"')
        return base_command

    @property
    def rest_url(self) -> str:
        return f'https://localhost:{self.rest_port}'

    @property
    def grpc_url(self) -> str:
        return f'localhost:{self.grpc_port}'

    def launch(self):
        command = self.lnd()
        command[0] = '"' + command[0] + '"'
        cmd = ' '.join(command)
        if IS_MACOS:
            with NamedTemporaryFile(suffix='-lnd.command', delete=False) as f:
                f.write(f'#!/bin/sh\n{cmd}\n'.encode('utf-8'))
                f.flush()
                call(['chmod', 'u+x', f.name])
                result = Popen(['open', '-W', f.name], close_fds=True)
        elif IS_WINDOWS:
            from subprocess import DETACHED_PROCESS, CREATE_NEW_PROCESS_GROUP
            with NamedTemporaryFile(suffix='-lnd.bat', delete=False) as f:
                f.write(cmd.encode('utf-8'))
                f.flush()
                result = Popen(
                    ['start', 'powershell', '-noexit', '-Command', f.name],
                    stdin=PIPE, stdout=PIPE, stderr=PIPE,
                    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                    close_fds=True, shell=True)
        elif IS_LINUX:
            with NamedTemporaryFile(suffix='-lnd.command', delete=False) as f:
                f.write(f'#!/bin/sh\n{cmd}\n'.encode('utf-8'))
                f.flush()
                call(['chmod', 'u+x', f.name])
                result = Popen(['gnome-terminal', '-e', f.name], close_fds=True)
        else:
            raise NotImplementedError()
        return result
