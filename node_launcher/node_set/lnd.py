import os
import socket
import ssl
import time
from signal import SIGINT, SIGTERM
from subprocess import call, Popen, PIPE
from sys import platform
from tempfile import NamedTemporaryFile
from typing import List, Optional

import psutil
from node_launcher.logging import log
from node_launcher.node_set.bitcoin import Bitcoin
from node_launcher.services.configuration_file import ConfigurationFile
from node_launcher.constants import (
    IS_LINUX,
    IS_MACOS,
    IS_WINDOWS,
    LND_DEFAULT_GRPC_PORT,
    LND_DEFAULT_PEER_PORT,
    LND_DEFAULT_REST_PORT,
    LND_DIR_PATH,
    OPERATING_SYSTEM
)
from node_launcher.services.lnd_software import LndSoftware
from node_launcher.utilities.utilities import get_port


class Lnd(object):
    file: ConfigurationFile
    software: LndSoftware
    process: Optional[psutil.Process]

    def __init__(self, configuration_file_path: str, bitcoin: Bitcoin):
        self.running = False
        self.is_unlocked = False
        self.bitcoin = bitcoin
        self.file = ConfigurationFile(configuration_file_path)
        self.process = self.find_running_node()
        self.software = LndSoftware()

        self.lnddir = LND_DIR_PATH[OPERATING_SYSTEM]

        # Previous versions of the launcher set lnddir in the config file,
        # but it is not a valid key so this helps old users upgrading
        if self.file['lnddir'] is not None:
            self.file['lnddir'] = None

        if self.file['debuglevel'] is None:
            self.file['debuglevel'] = 'info'

        self.file['bitcoin.active'] = True
        self.file['bitcoin.node'] = 'bitcoind'
        self.file['bitcoind.rpchost'] = f'127.0.0.1:{self.bitcoin.rpc_port}'
        self.file['bitcoind.rpcuser'] = self.bitcoin.file['rpcuser']
        self.file['bitcoind.rpcpass'] = self.bitcoin.file['rpcpassword']
        self.file['bitcoind.zmqpubrawblock'] = self.bitcoin.file[
            'zmqpubrawblock']
        self.file['bitcoind.zmqpubrawtx'] = self.bitcoin.file['zmqpubrawtx']

        if self.file['restlisten'] is None:
            if self.bitcoin.file['testnet']:
                self.rest_port = get_port(LND_DEFAULT_REST_PORT + 1)
            else:
                self.rest_port = get_port(LND_DEFAULT_REST_PORT)
            self.file['restlisten'] = f'127.0.0.1:{self.rest_port}'
        else:
            self.rest_port = self.file['restlisten'].split(':')[-1]

        if not self.file['rpclisten']:
            if self.bitcoin.file['testnet']:
                self.grpc_port = get_port(LND_DEFAULT_GRPC_PORT + 1)
            else:
                self.grpc_port = get_port(LND_DEFAULT_GRPC_PORT)
            self.file['rpclisten'] = f'127.0.0.1:{self.grpc_port}'
        else:
            self.grpc_port = int(self.file['rpclisten'].split(':')[-1])

        if self.file['color'] is None:
            self.file['color'] = '#000000'

        self.macaroon_path = os.path.join(
            self.lnddir,
            'data',
            'chain',
            'bitcoin',
            str(self.bitcoin.network)
        )
        self.config_snapshot = self.file.snapshot.copy()
        self.file.file_watcher.fileChanged.connect(self.config_file_changed)
        self.bitcoin.file.file_watcher.fileChanged.connect(self.bitcoin_config_file_changed)

    @property
    def node_port(self) -> str:
        if self.file['listen'] is None:
            if self.bitcoin.file['testnet']:
                port = get_port(LND_DEFAULT_PEER_PORT + 1)
            else:
                port = get_port(LND_DEFAULT_PEER_PORT)
            self.file['listen'] = f'127.0.0.1:{port}'
        else:
            if not isinstance(self.file['listen'], list):
                port = self.file['listen'].split(':')[-1]
            else:
                port = self.file['listen'][0].split(':')[-1]
        return port

    def test_tls_cert(self):
        context = ssl.create_default_context()
        context.load_verify_locations(cafile=self.tls_cert_path)
        conn = context.wrap_socket(socket.socket(socket.AF_INET),
                                   server_hostname='127.0.0.1')
        conn.connect(('127.0.0.1', int(self.rest_port)))
        cert = conn.getpeercert()
        return cert

    def check_process(self):
        if (self.process is None
                or not self.process.is_running()
                or not self.is_unlocked):
            self.find_running_node()

    def stop(self):
        self.check_process()
        if platform == 'win32':
            self.process.send_signal(SIGTERM)
        else:
            self.process.send_signal(SIGINT)
        time.sleep(0.1)
        self.check_process()
        if self.process is not None:
            self.stop()

    def find_running_node(self) -> Optional[psutil.Process]:
        self.is_unlocked = False
        self.running = False
        self.process = None
        found_ports = []
        try:
            processes = psutil.process_iter()
        except:
            log.warning(
                'Lnd.find_running_node',
                exc_info=True
            )
            return None

        for process in processes:
            if not process.is_running():
                log.warning(
                    'Lnd.find_running_node',
                    exc_info=True
                )
                continue
            try:
                process_name = process.name()
            except:
                log.warning(
                    'Lnd.find_running_node',
                    exc_info=True
                )
                continue
            if 'lnd' in process_name:
                lnd_process = process
                open_files = None
                try:
                    open_files = lnd_process.open_files()
                    log_file = open_files[0]
                except:
                    log.warning(
                        'Lnd.find_running_node',
                        open_files=open_files,
                        exc_info=True
                    )
                    continue
                if str(self.bitcoin.network) not in log_file.path:
                    continue
                self.process = lnd_process
                self.running = True
                try:
                    is_unlocked = False
                    connections = process.connections()
                    for connection in connections:
                        found_ports.append((connection.laddr, connection.raddr))
                        if 8080 <= connection.laddr.port <= 9000:
                            self.rest_port = connection.laddr.port
                        elif 10009 <= connection.laddr.port <= 10100:
                            self.grpc_port = connection.laddr.port
                        elif 9735 <= connection.laddr.port < 9800:
                            self.node_port = connection.laddr.port
                            is_unlocked = True
                    self.is_unlocked = is_unlocked
                    return lnd_process
                except:
                    log.warning(
                        'Lnd.find_running_node',
                        exc_info=True
                    )
                    continue
        return None

    @property
    def admin_macaroon_path(self) -> str:
        path = os.path.join(self.macaroon_path, 'admin.macaroon')
        return path

    @property
    def wallet_path(self) -> str:
        wallet_path = os.path.join(self.macaroon_path, 'wallet.db')
        return wallet_path

    @property
    def has_wallet(self) -> bool:
        return os.path.isfile(self.wallet_path)

    @property
    def tls_cert_path(self) -> str:
        tls_cert_path = os.path.join(self.lnddir, 'tls.cert')
        return tls_cert_path

    def lnd(self) -> List[str]:
        command = [
            self.software.lnd,
            f'--configfile="{self.file.path}"'
        ]
        if self.bitcoin.file['testnet']:
            command += [
                '--bitcoin.testnet'
            ]
        else:
            command += [
                '--bitcoin.mainnet'
            ]
        log.info(
            'lnd',
            command=command,
            **self.file.cache
        )
        return command

    def lncli_arguments(self) -> List[str]:
        args = []
        if self.grpc_port != LND_DEFAULT_GRPC_PORT:
            args.append(f'--rpcserver=127.0.0.1:{self.grpc_port}')
        if self.bitcoin.file['testnet']:
            args.append(f'--network={self.bitcoin.network}')
        if self.lnddir != LND_DIR_PATH[OPERATING_SYSTEM]:
            args.append(f'''--lnddir="{self.lnddir}"''')
            args.append(f'--macaroonpath="{self.macaroon_path}"')
            args.append(f'--tlscertpath="{self.tls_cert_path}"')
        return args

    @property
    def lncli(self) -> str:
        base_command = [
            f'"{self.software.lncli}"',
        ]
        base_command += self.lncli_arguments()
        return ' '.join(base_command)

    @property
    def rest_url(self) -> str:
        return f'https://127.0.0.1:{self.rest_port}'

    @property
    def grpc_url(self) -> str:
        return f'127.0.0.1:{self.grpc_port}'

    def launch(self):
        self.config_snapshot = self.file.snapshot.copy()
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

    def config_file_changed(self):
        # Refresh config file
        self.file.file_watcher.blockSignals(True)
        self.file.populate_cache()
        self.file.file_watcher.blockSignals(False)
        self.rest_port = int(self.file['restlisten'].split(':')[-1])
        self.grpc_port = int(self.file['rpclisten'].split(':')[-1])

        # Some text editors do not modify the file, they delete and replace the file
        # Check if file is still in file_watcher list of files, if not add back
        files_watched = self.file.file_watcher.files()
        if len(files_watched) == 0:
            self.file.file_watcher.addPath(self.file.path)

    def bitcoin_config_file_changed(self):
        # Refresh config file
        self.file.file_watcher.blockSignals(True)
        self.file.populate_cache()
        self.file.file_watcher.blockSignals(False)
        self.file['bitcoind.rpchost'] = f'127.0.0.1:{self.bitcoin.rpc_port}'
        self.file['bitcoind.rpcuser'] = self.bitcoin.file['rpcuser']
        self.file['bitcoind.rpcpass'] = self.bitcoin.file['rpcpassword']
        self.file['bitcoind.zmqpubrawblock'] = self.bitcoin.file['zmqpubrawblock']
        self.file['bitcoind.zmqpubrawtx'] = self.bitcoin.file['zmqpubrawtx']

    @property
    def restart_required(self):
        if self.running:
            # Did bitcoin details change
            if self.bitcoin.restart_required:
                return True and self.running

            old_config = self.config_snapshot.copy()
            new_config = self.file.snapshot

            fields = [
                'restlisten', 'listen', 'rpclisten'
            ]

            for field in fields:
                # First check if field is found in both configs
                found_in_old_config = field in old_config.keys()
                found_in_new_config = field in new_config.keys()
                if found_in_old_config != found_in_new_config:
                    return True

                # Now check that values are the same
                if found_in_old_config:
                    if old_config[field] != new_config[field]:
                        return True

        return False
