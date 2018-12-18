import os
import psutil
from subprocess import call, Popen, PIPE
from tempfile import NamedTemporaryFile
from typing import List, Optional

from psutil import ZombieProcess, AccessDenied

from node_launcher.node_set.bitcoin import Bitcoin
from node_launcher.services.configuration_file import ConfigurationFile
from node_launcher.constants import LND_DIR_PATH, OPERATING_SYSTEM, DARWIN, IS_WINDOWS
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

        self.lnddir = LND_DIR_PATH[OPERATING_SYSTEM]
        if not os.path.exists(self.lnddir):
            os.mkdir(self.lnddir)

        self.rest_port = get_port(8080)
        self.node_port = get_port(9735)
        self.grpc_port = get_port(10009)

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
        macaroons_path = os.path.join(self.lnddir, 'data', 'chain',
                                      'bitcoin', self.network)
        return macaroons_path

    @property
    def admin_macaroon_path(self) -> str:
        path = os.path.join(self.macaroon_path, 'admin.macaroon')
        return path

    @property
    def tls_cert_path(self) -> str:
        tls_cert_path = os.path.join(self.lnddir, 'tls.cert')
        return tls_cert_path

    def lnd(self) -> List[str]:
        command = [
            self.software.lnd,
            f'--lnddir="{self.lnddir}"',
            '--debuglevel=info',
            '--bitcoin.active',
            '--bitcoin.node=bitcoind',
            '--bitcoind.rpchost=127.0.0.1',
            f'--bitcoind.rpcuser={self.bitcoin.file.rpcuser}',
            f'--bitcoind.rpcpass={self.bitcoin.file.rpcpassword}',
            f'--bitcoind.zmqpubrawblock=tcp://127.0.0.1:{self.bitcoin.zmq_block_port}',
            f'--bitcoind.zmqpubrawtx=tcp://127.0.0.1:{self.bitcoin.zmq_tx_port}',
            f'--rpclisten=localhost:{self.grpc_port}',
            f'--restlisten=127.0.0.1:{self.rest_port}',
            f'--listen=127.0.0.1:{self.node_port}'
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
        if self.lnddir != LND_DIR_PATH[OPERATING_SYSTEM]:
            base_command.append(f'--lnddir="{self.lnddir}"')
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
        if OPERATING_SYSTEM == DARWIN:
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
        else:
            raise NotImplementedError()
        return result
