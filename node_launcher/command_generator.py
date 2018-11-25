from typing import List

from node_launcher.configuration import Configuration
from node_launcher.constants import WINDOWS, OPERATING_SYSTEM


class CommandGenerator(object):
    def __init__(self, testnet_conf, mainnet_conf):
        self.testnet = testnet_conf
        self.mainnet = mainnet_conf

    def bitcoin_qt(self, n: Configuration) -> List[str]:
        dir_arg = f'-datadir={n.dir.bitcoin_data()}'
        if OPERATING_SYSTEM == WINDOWS:
            dir_arg = f'-datadir="{n.dir.bitcoin_data()}"'
        command = [
            n.dir.bitcoin_qt(),
            dir_arg,
            '-prune=600',
            '-txindex=0',
            '-server=1',
            '-disablewallet=1',
            f'-rpcuser={n.bitcoin_rpc_user}',
            f'-rpcpassword={n.bitcoin_rpc_password}',
            f'-zmqpubrawblock=tcp://127.0.0.1:{n.ports.zmq_block}',
            f'-zmqpubrawtx=tcp://127.0.0.1:{n.ports.zmq_tx}'
        ]
        return command

    def testnet_bitcoin_qt(self) -> List[str]:
        return self.bitcoin_qt(self.testnet) + [
            '-testnet=1',
        ]

    def mainnet_bitcoin_qt(self) -> List[str]:
        return self.bitcoin_qt(self.mainnet)

    def lnd(self, n: Configuration) -> List[str]:
        dir_arg = f'--lnddir="{n.dir.lnd_data()}"'
        if OPERATING_SYSTEM == WINDOWS:
            dir_arg = f'--lnddir="{n.dir.lnd_data()}"'
        return [
            n.dir.lnd(),
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
