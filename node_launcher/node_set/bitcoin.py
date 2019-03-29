import os
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
from typing import Optional, List

import psutil

from node_launcher.exceptions import ZmqPortsNotOpenError
from node_launcher.logging import log
from node_launcher.services.bitcoin_software import BitcoinSoftware
from node_launcher.services.configuration_file import ConfigurationFile
from node_launcher.constants import (
    BITCOIN_DATA_PATH,
    OPERATING_SYSTEM,
    IS_WINDOWS,
    TESTNET_PRUNE,
    MAINNET_PRUNE,
    TESTNET, MAINNET, BITCOIN_MAINNET_PEER_PORT, BITCOIN_MAINNET_RPC_PORT,
    BITCOIN_TESTNET_RPC_PORT, BITCOIN_TESTNET_PEER_PORT)
from node_launcher.services.hard_drives import HardDrives
from node_launcher.utilities.utilities import get_random_password, get_zmq_port


class Bitcoin(object):
    file: ConfigurationFile
    hard_drives: HardDrives
    process: Optional[psutil.Process]
    software: BitcoinSoftware
    zmq_block_port: int
    zmq_tx_port: int

    def __init__(self, configuration_file_path: str):
        self.hard_drives = HardDrives()
        self.software = BitcoinSoftware()
        self.file = ConfigurationFile(configuration_file_path)
        self.running = False
        self.process = None

        if self.file['datadir'] is None:
            self.autoconfigure_datadir()

        if 'bitcoin.conf' in os.listdir(self.file['datadir']):
            actual_conf_file = os.path.join(self.file['datadir'], 'bitcoin.conf')
            log.info(
                'datadir_redirect',
                configuration_file_path=configuration_file_path,
                actual_conf_file=actual_conf_file
            )
            self.file = ConfigurationFile(actual_conf_file)
            if self.file['datadir'] is None:
                self.autoconfigure_datadir()

        self.wallet_paths = self.get_wallet_paths()

        if self.file['server'] is None:
            self.file['server'] = True

        if self.file['disablewallet'] is None and not self.wallet_paths:
            self.file['disablewallet'] = True
        elif self.file['disablewallet'] is None and self.wallet_paths:
            self.file['disablewallet'] = False

        if self.file['timeout'] is None:
            self.file['timeout'] = 6000

        if self.file['rpcuser'] is None:
            self.file['rpcuser'] = 'default_user'

        if self.file['rpcpassword'] is None:
            self.file['rpcpassword'] = get_random_password()

        if self.file['prune'] is None:
            should_prune = self.hard_drives.should_prune(self.file['datadir'],
                                                         has_bitcoin=True)
            self.set_prune(should_prune)

        if not self.detect_zmq_ports():
            self.zmq_block_port = get_zmq_port()
            self.zmq_tx_port = get_zmq_port()

        self.file['zmqpubrawblock'] = f'tcp://127.0.0.1:{self.zmq_block_port}'
        self.file['zmqpubrawtx'] = f'tcp://127.0.0.1:{self.zmq_tx_port}'

        # noinspection PyBroadException
        try:
            memory = psutil.virtual_memory()
            free_mb = round(memory.available / 1000000)
            free_mb -= int(free_mb * .3)
            self.file['dbcache'] = free_mb
        except:
            log.warning(
                'dbcache psutil.virtual_memory',
                exc_info=True
            )
            self.file['dbcache'] = 1000

        self.check_process()

    @property
    def network(self):
        if self.file['testnet']:
            return TESTNET
        return MAINNET

    def get_wallet_paths(self):
        exclude_files = {
            'addr.dat',
            'banlist.dat',
            'fee_estimates.dat',
            'mempool.dat',
            'peers.dat'
        }
        candidate_paths = []
        datadir = self.file['datadir']
        for file in os.listdir(datadir):
            if file not in exclude_files:
                path = os.path.join(datadir, file)
                candidate_paths.append(path)
        default_walletdir = os.path.join(self.file['datadir'], 'wallets')
        if os.path.exists(default_walletdir):
            for file in os.listdir(default_walletdir):
                if file not in exclude_files:
                    candidate_paths.append(
                        os.path.join(default_walletdir, file))
        if self.file['walletdir'] is not None:
            wallet_dir = self.file['walletdir']
            for file in os.listdir(wallet_dir):
                if file not in exclude_files:
                    candidate_paths += os.path.join(
                        os.path.join(wallet_dir, file))
        dat_files = [f for f in candidate_paths if f.endswith('.dat')
                     and not f.startswith('blk')]
        dat_files = set(dat_files)
        wallet_paths = set(dat_files - exclude_files)
        if self.file['wallet'] is not None:
            if isinstance(self.file['wallet'], list):
                for wallet in self.file['wallet']:
                    wallet_paths.add(wallet)
            else:
                wallet_paths.add(self.file['wallet'])
        return wallet_paths

    @property
    def node_port(self):
        if self.file['testnet']:
            return BITCOIN_TESTNET_PEER_PORT
        return BITCOIN_MAINNET_PEER_PORT

    @property
    def rpc_port(self):
        if self.file['testnet']:
            return BITCOIN_TESTNET_RPC_PORT
        return BITCOIN_MAINNET_RPC_PORT

    def set_prune(self, should_prune: bool = None):

        if should_prune is None:
            should_prune = self.hard_drives.should_prune(self.file['datadir'],
                                                         has_bitcoin=True)
        if should_prune:
            if self.file['testnet']:
                prune = TESTNET_PRUNE
            else:
                prune = MAINNET_PRUNE
            self.file['prune'] = prune
        else:
            self.file['prune'] = 0
        self.file['txindex'] = not should_prune

    def autoconfigure_datadir(self):
        default_datadir = BITCOIN_DATA_PATH[OPERATING_SYSTEM]
        big_drive = self.hard_drives.get_big_drive()
        default_is_big_enough = not self.hard_drives.should_prune(
            input_directory=default_datadir,
            has_bitcoin=True
        )
        default_is_biggest = self.hard_drives.is_default_partition(big_drive)
        log.info(
            'autoconfigure_datadir',
            default_is_big_enough=default_is_big_enough,
            default_is_biggest=default_is_biggest
        )
        if default_is_big_enough or default_is_biggest:
            self.file['datadir'] = default_datadir
            log.info(
                'autoconfigure_datadir',
                datadir=default_datadir
            )
            return

        if not self.hard_drives.should_prune(big_drive.mountpoint, False):
            datadir = os.path.join(big_drive.mountpoint, 'Bitcoin')
            self.file['datadir'] = datadir
            log.info(
                'autoconfigure_datadir',
                datadir=datadir
            )
            if not os.path.exists(self.file['datadir']):
                os.mkdir(self.file['datadir'])
        else:
            self.file['datadir'] = default_datadir
            log.info(
                'autoconfigure_datadir',
                datadir=default_datadir
            )

    def check_process(self):
        if self.process is not None:
            if (not self.process.is_running()
                    or self.process.status() == 'zombie'):
                self.process = None

        if self.process is None:
            self.running = False
            self.process = self.find_running_node()
            self.detect_zmq_ports()

    def find_running_node(self) -> Optional[psutil.Process]:
        # noinspection PyBroadException
        try:
            processes = psutil.process_iter()
        except:
            log.warning(
                'Bitcoin.find_running_node',
                exc_info=True
            )
            return None
        for process in processes:
            try:
                if not process.is_running() or process.status() == 'zombie':
                    continue
            except:
                log.warning(
                    'Bitcoin.find_running_node',
                    exc_info=True
                )
                continue
            # noinspection PyBroadException
            try:
                process_name = process.name()
            except:
                log.warning(
                    'Bitcoin.find_running_node',
                    exc_info=True
                )
                continue
            if 'bitcoin' in process_name:
                # noinspection PyBroadException
                try:
                    for connection in process.connections():
                        ports = [self.rpc_port, self.node_port]
                        if connection.laddr.port in ports:
                            self.running = True
                            return process
                except:
                    log.warning(
                        'Bitcoin.find_running_node',
                        exc_info=True
                    )
                    continue
        return None

    def detect_zmq_ports(self) -> bool:
        if self.process is None:
            return False
        ports = [c.laddr.port for c in self.process.connections()
                 if 18500 <= c.laddr.port <= 18600]
        ports = set(ports)
        if len(ports) != 2:
            raise ZmqPortsNotOpenError(
                'ZMQ ports are not open on your node, '
                'please close Bitcoin Core and launch it with the Node Launcher'
            )
        self.zmq_block_port = min(ports)
        self.zmq_tx_port = max(ports)
        self.file['zmqpubrawblock'] = f'tcp://127.0.0.1:{self.zmq_block_port}'
        self.file['zmqpubrawtx'] = f'tcp://127.0.0.1:{self.zmq_tx_port}'
        return True

    def bitcoin_qt(self) -> List[str]:
        command = [self.software.bitcoin_qt]
        args = [
            f'-conf={self.file.path}',
        ]
        if IS_WINDOWS:
            args = [
                f'-conf="{self.file.path}"',
            ]
        command += args
        log.info(
            'bitcoin_qt',
            command=command,
            **self.file.cache
        )
        return command

    def bitcoin_cli_arguments(self) -> List[str]:
        return [f'-conf={self.file.path}']

    @property
    def bitcoin_cli(self) -> str:
        command = [
            f'"{self.software.bitcoin_cli}"',
            f'-conf="{self.file.path}"',
        ]
        return ' '.join(command)

    def launch(self):
        command = self.bitcoin_qt()
        if IS_WINDOWS:
            from subprocess import DETACHED_PROCESS, CREATE_NEW_PROCESS_GROUP
            command[0] = '"' + command[0] + '"'
            cmd = ' '.join(command)
            with NamedTemporaryFile(suffix='-btc.bat', delete=False) as f:
                f.write(cmd.encode('utf-8'))
                f.flush()
                result = Popen(
                    ['start', 'powershell', '-noexit', '-windowstyle', 'hidden',
                     '-Command', f.name],
                    stdin=PIPE, stdout=PIPE, stderr=PIPE,
                    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                    close_fds=True, shell=True)
        else:
            result = Popen(command, close_fds=True, shell=False)

        return result
