import platform
from random import choice
from string import ascii_lowercase, digits
from typing import List

from node_launcher.constants import BITCOIN_QT_PATH
from node_launcher.networking_configuration import NetworkingConfiguration


class CommandGenerator(object):
    def __init__(self):
        self.operating_system = platform.system()
        self.bitcoin_rpc_user = 'user'
        self.bitcoin_rpc_password = ''.join(choice(ascii_lowercase + digits)
                                            for _ in range(16))
        self.testnet = NetworkingConfiguration()
        self.mainnet = NetworkingConfiguration()

    def bitcoin_qt(self, n: NetworkingConfiguration) -> List[str]:
        command = [
            BITCOIN_QT_PATH[self.operating_system],
            '-prune=600',
            '-txindex=0',
            '-server=1',
            '-disablewallet=1',
            f'-rpcuser={self.bitcoin_rpc_user}',
            f'-rpcpassword={self.bitcoin_rpc_password}',
            f'-zmqpubrawblock=tcp://127.0.0.1:{n.zmq_block_port}',
            f'-zmqpubrawtx=tcp://127.0.0.1:{n.zmq_tx_port}'
        ]
        return command

    def testnet_bitcoin_qt(self) -> List[str]:
        return self.bitcoin_qt(self.testnet) + [
                   '-testnet=1',
               ]

    def mainnet_bitcoin_qt(self) -> List[str]:
        return self.bitcoin_qt(self.mainnet)

    def lnd_binary(self) -> str:
        return ''

    def lnd(self, n: NetworkingConfiguration) -> List[str]:
        return [
            self.lnd_binary(),
            '--debuglevel=info',
            '--bitcoin.active',
            '--bitcoin.node=bitcoind',
            '--bitcoind.rpchost=127.0.0.1',
            '--bitcoind.rpcuser=test_user',
            f'--bitcoind.rpcpass={self.bitcoin_rpc_password}',
            f'--bitcoind.zmqpubrawblock=tcp://127.0.0.1:{n.zmq_block_port}',
            f'--bitcoind.zmqpubrawtx=tcp://127.0.0.1:{n.zmq_tx_port}',
            f'--rpclisten=localhost:{n.grpc_port}',
            f'--restlisten=0.0.0.0:{n.rest_port}',
            f'--listen=0.0.0.0:{n.node_port}'
        ]

    def testnet_lnd(self) -> List[str]:
        return self.lnd(self.testnet) + [
            '--bitcoin.testnet'
        ]
