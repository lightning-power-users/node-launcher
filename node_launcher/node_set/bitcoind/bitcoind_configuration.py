import os
from typing import List

import psutil

from node_launcher.constants import (
    OPERATING_SYSTEM,
    BITCOIN_DATA_PATH,
    BITCOIN_MAINNET_PEER_PORT,
    BITCOIN_MAINNET_RPC_PORT, MAINNET_PRUNE
)
from node_launcher.app_logging import log
from node_launcher.node_set.lib.configuration import Configuration
from node_launcher.node_set.lib.get_random_password import get_random_password
from node_launcher.node_set.lib.hard_drives import Partition
from node_launcher.node_set.bitcoind.bitcoind_configuration_keys import keys_info as bitcoind_keys_info
from node_launcher.port_utilities import get_zmq_port


class BitcoindConfiguration(Configuration):
    zmq_block_port: int
    zmq_tx_port: int
    partition: Partition

    def __init__(self, partition: Partition):
        self.partition = partition
        file_name = 'bitcoin.conf'
        bitcoin_data_path = BITCOIN_DATA_PATH[OPERATING_SYSTEM]
        configuration_file_path = os.path.join(bitcoin_data_path, file_name)
        super().__init__(name='bitcoind', path=configuration_file_path, keys_info=bitcoind_keys_info)

    @property
    def args(self) -> List[str]:
        return [f'-conf={self.file.path}']

    @property
    def cli_args(self) -> List[str]:
        return self.args

    def check(self):
        log.debug('datadir', datadir=self['datadir'])

        if ('datadir' not in self
                or not os.path.exists(self['datadir'])):
            self['datadir'] = self.partition.bitcoin_dir_path

        if os.path.exists(os.path.join(self['datadir'], 'blocks')):
            if 'prune' not in self:
                self.set_prune(False)
        else:
            if 'prune' not in self:
                should_prune = not self.partition.can_archive
                self.set_prune(should_prune)

        self['txindex'] = 1
        self['reindex'] = 0

        self.set_default_configuration('server', True)

        self.set_default_configuration('timeout', 6000)

        self.set_default_configuration('rpcuser', 'default_user')
        self.set_default_configuration('rpcpassword', get_random_password())

        self['blockfilterindex'] = True

        self.zmq_block_port = get_zmq_port()
        self.zmq_tx_port = get_zmq_port()

        self['zmqpubrawblock'] = f'tcp://127.0.0.1:{self.zmq_block_port}'
        self['zmqpubrawtx'] = f'tcp://127.0.0.1:{self.zmq_tx_port}'

        self['proxy'] = '127.0.0.1:9050'
        self['listen'] = True
        self['bind'] = '127.0.0.1'
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

    def set_prune(self, should_prune: bool):
        if should_prune:
            self['prune'] = MAINNET_PRUNE
        else:
            self['prune'] = 0
        self['txindex'] = not should_prune

    @property
    def node_port(self):
        custom_port = self['port']
        if custom_port is not None:
            return custom_port
        return BITCOIN_MAINNET_PEER_PORT

    @property
    def rpc_port(self):
        if self['rpcport'] is not None:
            return self['rpcport']
        return BITCOIN_MAINNET_RPC_PORT
