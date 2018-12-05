from typing import List

from node_launcher.configuration import Configuration
from node_launcher.constants import OPERATING_SYSTEM, LND_DIR_PATH, IS_WINDOWS


class CommandGenerator(object):
    mainnet: Configuration
    testnet: Configuration

    def __init__(self, testnet_conf: Configuration, mainnet_conf: Configuration):
        self.testnet = testnet_conf
        self.mainnet = mainnet_conf

    @staticmethod
    def bitcoin_qt(n: Configuration) -> List[str]:
        dir_arg = f'-datadir={n.bitcoin.file.datadir}'
        if IS_WINDOWS:
            dir_arg = f'-datadir="{n.bitcoin.file.datadir}"'
        command = [
            n.bitcoin.software.bitcoin_qt,
            dir_arg,
            '-server=1',
            '-disablewallet=1',
            f'-rpcuser={n.bitcoin.file.rpcuser}',
            f'-rpcpassword={n.bitcoin.file.rpcpassword}',
            f'-zmqpubrawblock=tcp://127.0.0.1:{n.bitcoin.zmq_block_port}',
            f'-zmqpubrawtx=tcp://127.0.0.1:{n.bitcoin.zmq_tx_port}'
        ]
        if n.bitcoin.file.prune:
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
            n.lnd.software.lnd,
            f'--lnddir="{n.lnd.lnddir}"',
            '--debuglevel=info',
            '--bitcoin.active',
            '--bitcoin.node=bitcoind',
            '--bitcoind.rpchost=127.0.0.1',
            f'--bitcoind.rpcuser={n.bitcoin.file.rpcuser}',
            f'--bitcoind.rpcpass={n.bitcoin.file.rpcpassword}',
            f'--bitcoind.zmqpubrawblock=tcp://127.0.0.1:{n.bitcoin.zmq_block_port}',
            f'--bitcoind.zmqpubrawtx=tcp://127.0.0.1:{n.bitcoin.zmq_tx_port}',
            f'--rpclisten=localhost:{n.lnd.grpc_port}',
            f'--restlisten=127.0.0.1:{n.lnd.rest_port}',
            f'--listen=127.0.0.1:{n.lnd.node_port}'
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
            f'"{n.lnd.software.lncli}"',
        ]
        if n.lnd.grpc_port != 10009:
            base_command.append(f'--rpcserver=localhost:{n.lnd.grpc_port}')
        if n.network != 'mainnet':
            base_command.append(f'--network={n.network}')
        if n.lnd.lnddir != LND_DIR_PATH[OPERATING_SYSTEM]:
            base_command.append(f'--lnddir="{n.lnd.lnddir}"')
            base_command.append(f'--macaroonpath="{n.lnd.macaroon_path}"')
            base_command.append(f'--tlscertpath="{n.lnd.tls_cert_path}"')
        return base_command

    def testnet_lncli(self) -> List[str]:
        return self.lncli(self.testnet)

    def mainnet_lncli(self) -> List[str]:
        return self.lncli(self.mainnet)

    def testnet_rest_url(self) -> str:
        return f'https://localhost:{self.testnet.lnd.rest_port}'

    def mainnet_rest_url(self) -> str:
        return f'https://localhost:{self.mainnet.lnd.rest_port}'
