import os
from typing import List

import psutil

from node_launcher.constants import (
    OPERATING_SYSTEM,
    BITCOIN_DATA_PATH,
    BITCOIN_MAINNET_PEER_PORT,
    BITCOIN_MAINNET_RPC_PORT,
    MAINNET_PRUNE
)
from node_launcher.logging import log
from node_launcher.node_set.lib.configuration import Configuration
from node_launcher.node_set.lib.get_random_password import get_random_password
from node_launcher.node_set.lib.hard_drives import HardDrives
from node_launcher.port_utilities import get_zmq_port


class BitcoindConfiguration(Configuration):
    hard_drives: HardDrives
    zmq_block_port: int
    zmq_tx_port: int

    def __init__(self):
        self.hard_drives = HardDrives()
        file_name = 'bitcoin.conf'
        bitcoin_data_path = BITCOIN_DATA_PATH[OPERATING_SYSTEM]
        configuration_file_path = os.path.join(bitcoin_data_path, file_name)
        super().__init__(name='bitcoind', path=configuration_file_path)

    @property
    def args(self) -> List[str]:
        return [f'-conf={self.file.path}']

    @property
    def cli_args(self) -> List[str]:
        return self.args

    def check(self):
        log.debug('datadir', datadir=self['datadir'])

        if (self['datadir'] is None
                or not os.path.exists(self['datadir'])):
            self.autoconfigure_datadir()

        if os.path.exists(os.path.join(self['datadir'], 'blocks')):
            if self['prune'] is None:
                self.set_prune(False)
        else:
            if self['prune'] is None:
                should_prune = self.hard_drives.should_prune(self['datadir'])
                self.set_prune(should_prune)

        self.wallet_paths = self.get_wallet_paths()

        if self['server'] is None:
            self['server'] = True

        if self['disablewallet'] is None and not self.wallet_paths:
            self['disablewallet'] = True
        elif self['disablewallet'] is None and self.wallet_paths:
            self['disablewallet'] = False

        if self['timeout'] is None:
            self['timeout'] = 6000

        if self['rpcuser'] is None:
            self['rpcuser'] = 'default_user'

        if self['rpcpassword'] is None:
            self['rpcpassword'] = get_random_password()

        self.zmq_block_port = get_zmq_port()
        self.zmq_tx_port = get_zmq_port()

        self['zmqpubrawblock'] = f'tcp://127.0.0.1:{self.zmq_block_port}'
        self['zmqpubrawtx'] = f'tcp://127.0.0.1:{self.zmq_tx_port}'

        self['proxy'] = '127.0.0.1:9050'
        self['listen'] = True
        self['bind'] = '127.0.0.1'
        self['debug'] = 'tor'
        self['discover'] = True

        # noinspection PyBroadException
        try:
            memory = psutil.virtual_memory()
            free_mb = round(memory.available / 1000000)
            free_mb -= int(free_mb * .3)
            self['dbcache'] = min(free_mb, 10000)
            self['maxmempool'] = 500
            self['mempoolexpiry'] = 2000
        except:
            log.warning(
                'dbcache psutil.virtual_memory',
                exc_info=True
            )
            self['dbcache'] = 1000

        # self.config_snapshot = self.snapshot.copy()
        # self.file_watcher.fileChanged.connect(self.config_file_changed)

    def autoconfigure_datadir(self):
        default_datadir = BITCOIN_DATA_PATH[OPERATING_SYSTEM]
        big_drive = self.hard_drives.get_big_drive()
        default_is_big_enough = not self.hard_drives.should_prune(
            input_directory=default_datadir
        )
        default_is_biggest = self.hard_drives.is_default_partition(big_drive)
        log.info(
            'autoconfigure_datadir',
            default_is_big_enough=default_is_big_enough,
            default_is_biggest=default_is_biggest
        )
        if default_is_big_enough or default_is_biggest:
            self['datadir'] = default_datadir
            log.info(
                'autoconfigure_datadir',
                datadir=default_datadir
            )
            return

        if not self.hard_drives.should_prune(big_drive.mountpoint):
            datadir = os.path.join(big_drive.mountpoint, 'Bitcoin')
            self['datadir'] = datadir
            log.info(
                'autoconfigure_datadir',
                datadir=datadir
            )
            if not os.path.exists(self['datadir']):
                os.mkdir(self['datadir'])
        else:
            self['datadir'] = default_datadir
            log.info(
                'autoconfigure_datadir',
                datadir=default_datadir
            )

    def get_wallet_paths(self):
        exclude_files = {
            'addr.dat',
            'banlist.dat',
            'fee_estimates.dat',
            'mempool.dat',
            'peers.dat'
        }
        candidate_paths = []
        datadir = self['datadir']
        wallet_dir = self['main.walletdir']
        wallets = self['main.wallet']
        for file in os.listdir(datadir):
            if file not in exclude_files:
                path = os.path.join(datadir, file)
                candidate_paths.append(path)
        default_walletdir = os.path.join(datadir, 'wallets')
        if os.path.exists(default_walletdir):
            for file in os.listdir(default_walletdir):
                if file not in exclude_files:
                    candidate_paths.append(
                        os.path.join(default_walletdir, file))
        if wallet_dir is not None:
            for file in os.listdir(wallet_dir):
                if file not in exclude_files:
                    candidate_paths += os.path.join(
                        os.path.join(wallet_dir, file))
        dat_files = [f for f in candidate_paths if f.endswith('.dat')
                     and not f.startswith('blk')]
        dat_files = set(dat_files)
        wallet_paths = set(dat_files - exclude_files)
        if wallets is not None:
            if isinstance(wallets, list):
                for wallet in wallets:
                    wallet_paths.add(wallet)
            else:
                wallet_paths.add(wallets)
        return wallet_paths

    @property
    def node_port(self):
        custom_port = self['port']
        if custom_port is not None:
            return custom_port
        return BITCOIN_MAINNET_PEER_PORT

    @property
    def rpc_port(self):
        custom_port = self['rpcport']
        if custom_port is not None:
            return custom_port
        return BITCOIN_MAINNET_RPC_PORT

    def set_prune(self, should_prune: bool):
        if should_prune:
            self['prune'] = MAINNET_PRUNE
        else:
            self['prune'] = 0
        self['txindex'] = not should_prune

    def config_file_changed(self):
        # Refresh config file
        self.file_watcher.blockSignals(True)
        self.initialize_cache_and_model_repository()
        self.file_watcher.blockSignals(False)
        if self['zmqpubrawblock']:
            self.zmq_block_port = int(self['zmqpubrawblock'].split(':')[-1])
        if self['zmqpubrawtx']:
            self.zmq_tx_port = int(self['zmqpubrawtx'].split(':')[-1])
        # Some text editors do not modify the file, they delete and replace the file
        # Check if file is still in file_watcher list of files, if not add back
        files_watched = self.file_watcher.files()
        if len(files_watched) == 0:
            self.file_watcher.addPath(self.path)

    @property
    def restart_required(self):
        old_config = self.config_snapshot.copy()
        new_config = self.snapshot

        # First check that both config files are still on the same network
        old_config_network = 'testnet' in old_config.keys()
        new_config_network = 'testnet' in new_config.keys()

        if (old_config_network == new_config_network) and self.running:
            common_fields = [
                'rpcuser', 'rpcpassword', 'disablewallet', 'datadir', 'disablewallet',
                'zmqpubrawblock', 'zmqpubrawtx', 'prune', 'txindex', 'timeout'
            ]

            for field in common_fields:

                # First check if field is found in both configs
                found_in_old_config = field in old_config.keys()
                found_in_new_config = field in new_config.keys()
                if found_in_old_config != found_in_new_config:
                    return True

                # Now check that values are the same
                if found_in_old_config:
                    if old_config[field] != new_config[field]:
                        return True

            else:
                # Only check mainnet fields if currently running mainnet
                mainnet_fields = [
                    'rpcport', 'port'
                ]

                for field in mainnet_fields:
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
        elif self.running:
            # Network has changed and the node is running - Restart is required
            return True

        return False

