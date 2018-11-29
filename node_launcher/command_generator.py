from typing import List

from node_launcher.configuration import Configuration
from node_launcher.constants import WINDOWS, OPERATING_SYSTEM, LND_DATA_PATH


class CommandGenerator(object):
    mainnet: Configuration
    testnet: Configuration

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
            f'-rpcuser={n.bitcoin.rpcuser}',
            f'-rpcpassword={n.bitcoin.rpcpassword}',
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
        return [
            n.dir.lnd.lnd,
            f'--lnddir="{n.dir.lnd_data_path}"',
            '--debuglevel=info',
            '--bitcoin.active',
            '--bitcoin.node=bitcoind',
            '--bitcoind.rpchost=127.0.0.1',
            f'--bitcoind.rpcuser={n.bitcoin.rpcuser}',
            f'--bitcoind.rpcpass={n.bitcoin.rpcpassword}',
            f'--bitcoind.zmqpubrawblock=tcp://127.0.0.1:{n.ports.zmq_block}',
            f'--bitcoind.zmqpubrawtx=tcp://127.0.0.1:{n.ports.zmq_tx}',
            f'--rpclisten=localhost:{n.ports.grpc}',
            f'--restlisten=127.0.0.1:{n.ports.rest}',
            f'--listen=127.0.0.1:{n.ports.node}'
        ]

    def testnet_lnd(self) -> List[str]:
        return self.lnd(self.testnet) + [
            '--bitcoin.testnet'
        ]

    def mainnet_lnd(self) -> List[str]:
        return self.lnd(self.mainnet) + [
            '--bitcoin.mainnet'
        ]

    @staticmethod
    def lncli(n: Configuration):
        base_command = [
            f'"{n.dir.lnd.lncli}"',
        ]
        if n.ports.grpc != 10009:
            base_command.append(f'--rpcserver=localhost:{n.ports.grpc}')
        if n.network != 'mainnet':
            base_command.append(f'--network={n.network}')
        if n.dir.lnd_data_path != LND_DATA_PATH[OPERATING_SYSTEM]:
            base_command.append(f'--lnddir="{n.dir.lnd_data_path}"')
            base_command.append(f'--macaroonpath="{n.dir.macaroon_path(n.network)}"')
            base_command.append(f'--tlscertpath="{n.dir.tls_cert_path}"')
        return base_command

    def testnet_lncli(self) -> List[str]:
        return self.lncli(self.testnet)

    def mainnet_lncli(self) -> List[str]:
        return self.lncli(self.mainnet)

    def testnet_rest_url(self) -> str:
        return f'https://localhost:{self.testnet.ports.rest}'

    def mainnet_rest_url(self) -> str:
        return f'https://localhost:{self.mainnet.ports.rest}'
