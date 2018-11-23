import platform
from random import choice
from string import ascii_lowercase, digits
from typing import List

from node_launcher.constants import BITCOIN_QT_PATH


class CommandGenerator(object):
    operating_system: str

    def __init__(self):
        self.operating_system = platform.system()
        self.bitcoin_rpc_password = ''.join(choice(ascii_lowercase + digits)
                                            for _ in range(16))

    def bitcoin_qt(self) -> List[str]:
        command = [
            BITCOIN_QT_PATH[self.operating_system],
            '-prune=600',
            '-txindex=0',
            '-rpcuser=user',
            f'-rpcpassword={self.bitcoin_rpc_password}',
            '-server=1',
            '-disablewallet=1'
        ]
        return command

    def testnet_bitcoin_qt(self) -> List[str]:
        return self.bitcoin_qt() + [
            '-testnet=1',
            '-zmqpubrawblock=tcp://127.0.0.1:18501',
            '-zmqpubrawtx=tcp://127.0.0.1:18502'
        ]

    def mainnet_bitcoin_qt(self) -> List[str]:
        return self.bitcoin_qt() + [
            '-zmqpubrawblock=tcp://127.0.0.1:18503',
            '-zmqpubrawtx=tcp://127.0.0.1:18504'
        ]

    def lnd(self) -> List[str]:
        .\lnd.exe --bitcoin.active --bitcoin.testnet --bitcoin.node=bitcoind --bitcoind.rpchost=127.0.0.1 --bitcoind.rpcuser=test_user --bitcoind.rpcpass=YOURPASSWORD --bitcoind.zmqpubrawblock=tcp://127.0.0.1:18501 --bitcoind.zmqpubrawtx=tcp://127.0.0.1:18502 --debuglevel=info --rpclisten=localhost:10010 --restlisten=0.0.0.0:8081 --listen=0.0.0.0:9736

    def testnet_lnd(self) -> List[str]:
        return self.lnd() + [

        ]