from typing import List

from node_launcher.configuration import Configuration
from node_launcher.constants import WINDOWS, OPERATING_SYSTEM


class CommandGenerator(object):
    def __init__(self, testnet_conf: Configuration, mainnet_conf: Configuration):
        self.testnet = testnet_conf
        self.mainnet = mainnet_conf

    @staticmethod
    def bitcoin_qt(n: Configuration) -> List[str]:
        dir_arg = f'-datadir={n.bitcoin.datadir}'
        if OPERATING_SYSTEM == WINDOWS:
            dir_arg = f'-datadir="{n.bitcoin.datadir}"'
        command = [
            n.dir.bitcoin.bitcoin_qt,
            dir_arg,
            '-server=1',
            '-disablewallet=1',
            f'-rpcuser={n.bitcoin_rpc_user}',
            f'-rpcpassword={n.bitcoin_rpc_password}',
            f'-zmqpubrawblock=tcp://127.0.0.1:{n.ports.zmq_block}',
            f'-zmqpubrawtx=tcp://127.0.0.1:{n.ports.zmq_tx}'
        ]
        if n.bitcoin.prune:
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
            n.dir.lnd.lnd,
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
