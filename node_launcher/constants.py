import os
from os.path import expanduser
import platform
from typing import Dict

NODE_LAUNCHER_RELEASE = '.'.join(
    map(
        str,
        (
            7,
            0,
            0
        )
    )
)


class StringConstant(object):
    def __init__(self, name: str):
        self.name = name.lower()

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return str(other) == self.name

    def __ne__(self, other):
        return str(other).lower() != self.name

    def __repr__(self):
        return self.name


class NodeSoftwareName(StringConstant):
    pass


TOR: NodeSoftwareName = NodeSoftwareName('tor')
BITCOIND: NodeSoftwareName = NodeSoftwareName('bitcoind')
LND: NodeSoftwareName = NodeSoftwareName('lnd')
NODE_LAUNCHER: NodeSoftwareName = NodeSoftwareName('node-launcher')
TEST_SOFTWARE: NodeSoftwareName = NodeSoftwareName('test-software')


class Network(StringConstant):
    pass


TESTNET: Network = Network('testnet')
MAINNET: Network = Network('mainnet')


class OperatingSystem(StringConstant):
    pass


DARWIN: OperatingSystem = OperatingSystem('darwin')
LINUX: OperatingSystem = OperatingSystem('linux')
WINDOWS: OperatingSystem = OperatingSystem('windows')
OPERATING_SYSTEM = OperatingSystem(platform.system())

IS_MACOS = OPERATING_SYSTEM == DARWIN
IS_LINUX = OPERATING_SYSTEM == LINUX
IS_WINDOWS = OPERATING_SYSTEM == WINDOWS

NODE_LAUNCHER_DATA_PATH: Dict[OperatingSystem, str] = {}
TOR_DIR_PATH: Dict[OperatingSystem, str] = {}
BITCOIN_DATA_PATH: Dict[OperatingSystem, str] = {}
LND_DIR_PATH: Dict[OperatingSystem, str] = {}

if IS_WINDOWS:
    LOCALAPPDATA = os.path.abspath(os.environ.get('LOCALAPPDATA', ''))
    APPDATA = os.path.abspath(os.environ.get('APPDATA', ''))
    PROGRAMS = os.environ.get('Programw6432', '')
    NODE_LAUNCHER_DATA_PATH[WINDOWS] = os.path.join(LOCALAPPDATA, 'Node Launcher')
    TOR_DIR_PATH[WINDOWS] = os.path.join(APPDATA, 'tor')
    BITCOIN_DATA_PATH[WINDOWS] = os.path.join(APPDATA, 'Bitcoin')
    LND_DIR_PATH[WINDOWS] = os.path.join(LOCALAPPDATA, 'Lnd')
elif IS_LINUX:
    NODE_LAUNCHER_DATA_PATH[LINUX] = expanduser('~/.node_launcher')
    TOR_DIR_PATH[LINUX] = '/var/tmp/dist/tor/etc/tor/'
    BITCOIN_DATA_PATH[LINUX] = expanduser('~/.bitcoin')
    LND_DIR_PATH[LINUX] = expanduser('~/.lnd/')
elif IS_MACOS:
    NODE_LAUNCHER_DATA_PATH[DARWIN] = expanduser('~/Library/Application Support/Node Launcher/')
    TOR_DIR_PATH[DARWIN] = '/var/tmp/dist/tor/etc/tor/'
    BITCOIN_DATA_PATH[DARWIN] = expanduser('~/Library/Application Support/Bitcoin/')
    LND_DIR_PATH[DARWIN] = expanduser('~/Library/Application Support/Lnd/')

try:
    os.mkdir(os.path.join(NODE_LAUNCHER_DATA_PATH[OPERATING_SYSTEM]))
except FileExistsError:
    pass

TOR_SERVICE_PATH = os.path.join(NODE_LAUNCHER_DATA_PATH[OPERATING_SYSTEM], 'tor-service')

UPGRADE = 'Please download the latest version of the Node Launcher: ' \
          '<a href="https://github.com/PierreRochard/node-launcher/releases/">' \
          'https://github.com/PierreRochard/node-launcher/releases' \
          '</a>'

GIGABYTE = 1000000000

if IS_WINDOWS:
    from keyring.backends.Windows import WinVaultKeyring

    keyring = WinVaultKeyring()

if IS_MACOS:
    from keyring.backends.macOS import Keyring

    keyring = Keyring()

if IS_LINUX:
    from keyring.backends.SecretService import Keyring

    keyring = Keyring()

AUTOPRUNE_GB = 150
# How many megabytes to keep
# Total Bitcoin (mainnet) data directory size minus blocks is ~3 GB
# We are targeting 10 GB, so 10 - 3 = 7
MAINNET_PRUNE = 7000

MINIMUM_GB = 10
MAXIMUM_GB = 450


BITCOIN_TESTNET_PEER_PORT = 18333
BITCOIN_MAINNET_PEER_PORT = 8333

BITCOIN_TESTNET_RPC_PORT = 18332
BITCOIN_MAINNET_RPC_PORT = 8332

LND_DEFAULT_PEER_PORT = 9735
LND_DEFAULT_GRPC_PORT = 10009
LND_DEFAULT_REST_PORT = 8080

LNCLI_COMMANDS = [
    'abandonchannel',
    'addinvoice',
    'changepassword',
    'channelbalance',
    'closeallchannels',
    'closechannel',
    'closedchannels',
    'connect',
    'create',
    'debuglevel',
    'decodepayreq',
    'describegraph',
    'disconnect',
    'feereport',
    'fwdinghistory',
    'getchaninfo',
    'getinfo',
    'getnetworkinfo',
    'getnodeinfo',
    'help',
    'listchaintxns',
    'listchannels',
    'listinvoices',
    'listpayments',
    'listpeers',
    'lookupinvoice',
    'newaddress',
    'openchannel',
    'payinvoice',
    'pendingchannels',
    'queryroutes',
    'sendcoins',
    'sendmany',
    'sendpayment',
    'sendtoroute',
    'signmessage',
    'stop',
    'unlock',
    'updatechanpolicy',
    'verifymessage',
    'walletbalance'
]

BITCOIN_CLI_COMMANDS = [
    'getbestblockhash',
    'addnode',
    'clearbanned',
    'combinepsbt',
    'combinerawtransaction',
    'converttopsbt',
    'createmultisig',
    'createpsbt',
    'createrawtransaction',
    'decodepsbt',
    'decoderawtransaction',
    'decodescript',
    'disconnectnode',
    'estimatesmartfee',
    'finalizepsbt',
    'generatetoaddress',
    'getaddednodeinfo',
    'getblock',
    'getblockchaininfo',
    'getblockcount',
    'getblockhash',
    'getblockheader',
    'getblockstats',
    'getblocktemplate',
    'getchaintips',
    'getchaintxstats',
    'getconnectioncount',
    'getdifficulty',
    'getmemoryinfo',
    'getmempoolancestors',
    'getmempooldescendants',
    'getmempoolentry',
    'getmempoolinfo',
    'getmininginfo',
    'getnettotals',
    'getnetworkhashps',
    'getnetworkinfo',
    'getpeerinfo',
    'getrawmempool',
    'getrawtransaction',
    'gettxout',
    'gettxoutproof',
    'gettxoutsetinfo',
    'getzmqnotifications',
    'help',
    'listbanned',
    'logging',
    'ping',
    'preciousblock',
    'prioritisetransaction',
    'pruneblockchain',
    'savemempool',
    'scantxoutset',
    'sendrawtransaction',
    'setban',
    'setnetworkactive',
    'signmessagewithprivkey',
    'signrawtransaction',
    'signrawtransactionwithkey',
    'stop',
    'submitblock',
    'testmempoolaccept',
    'uptime',
    'validateaddress',
    'verifychain',
    'verifymessage',
    'verifytxoutproof'
]
