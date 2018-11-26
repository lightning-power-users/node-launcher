import math
import os
from shutil import disk_usage
from typing import List

from node_launcher.configuration import Configuration
from node_launcher.constants import WINDOWS, OPERATING_SYSTEM
from node_launcher.utilities import get_dir_size


class CommandGenerator(object):
    def __init__(self, testnet_conf, mainnet_conf):
        self.testnet = testnet_conf
        self.mainnet = mainnet_conf

    def should_prune(self) -> bool:
        _, _, free_bytes = disk_usage(
            os.path.realpath(self.mainnet.dir.bitcoin_data_path))
        bitcoin_bytes = get_dir_size(self.mainnet.dir.bitcoin_data_path)
        free_bytes += bitcoin_bytes
        gigabyte = 1000000000
        free_gb = math.floor(free_bytes / gigabyte)
        bitcoin_gb = math.ceil(bitcoin_bytes / gigabyte)
        if free_gb < 300 and bitcoin_gb > 10:
            raise Exception('Un-pruned bitcoin chain data '
                            'but not enough space to finish IBD')
        return free_gb < 300

    def bitcoin_qt(self, n: Configuration) -> List[str]:
        dir_arg = f'-datadir={n.dir.bitcoin_data_path}'
        if OPERATING_SYSTEM == WINDOWS:
            dir_arg = f'-datadir="{n.dir.bitcoin_data_path}"'
        command = [
            n.dir.bitcoin_qt,
            dir_arg,
            '-server=1',
            '-disablewallet=1',
            f'-rpcuser={n.bitcoin_rpc_user}',
            f'-rpcpassword={n.bitcoin_rpc_password}',
            f'-zmqpubrawblock=tcp://127.0.0.1:{n.ports.zmq_block}',
            f'-zmqpubrawtx=tcp://127.0.0.1:{n.ports.zmq_tx}'
        ]
        if self.should_prune():
            command += [
                '-prune=600',
                '-txindex=0'
            ]
        else:
            command += [
                '-prune=0',
                '-txindex=1'
            ]
        return command

    def testnet_bitcoin_qt(self) -> List[str]:
        return self.bitcoin_qt(self.testnet) + [
            '-testnet=1',
        ]

    def mainnet_bitcoin_qt(self) -> List[str]:
        return self.bitcoin_qt(self.mainnet) + [
            '-testnet=0',
        ]

    @staticmethod
    def lnd(n: Configuration) -> List[str]:
        dir_arg = f'--lnddir="{n.dir.lnd_data_path}"'
        if OPERATING_SYSTEM == WINDOWS:
            dir_arg = f'--lnddir="{n.dir.lnd_data_path}"'
        return [
            n.dir.lnd,
            dir_arg,
            '--debuglevel=info',
            '--bitcoin.active',
            '--bitcoin.node=bitcoind',
            '--bitcoind.rpchost=127.0.0.1',
            f'--bitcoind.rpcuser={n.bitcoin_rpc_user}',
            f'--bitcoind.rpcpass={n.bitcoin_rpc_password}',
            f'--bitcoind.zmqpubrawblock=tcp://127.0.0.1:{n.ports.zmq_block}',
            f'--bitcoind.zmqpubrawtx=tcp://127.0.0.1:{n.ports.zmq_tx}',
            f'--rpclisten=localhost:{n.ports.grpc}',
            f'--restlisten=0.0.0.0:{n.ports.rest}',
            f'--listen=0.0.0.0:{n.ports.node}'
        ]

    def testnet_lnd(self) -> List[str]:
        return self.lnd(self.testnet) + [
            '--bitcoin.testnet'
        ]

    def mainnet_lnd(self) -> List[str]:
        return self.lnd(self.mainnet) + [
            '--bitcoin.mainnet'
        ]
