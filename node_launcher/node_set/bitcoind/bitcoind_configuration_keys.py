
from functools import partial

from node_launcher.utilities.validators import is_binary, is_address_with_port, is_address, is_port, \
    is_positive_integer, is_non_empty, is_user_and_pass, is_ip_or_subnet, is_folder_path, is_ratio, \
    is_non_negative_integer, is_integer_in_range, is_tcp_address_with_port


# TODO: Add all keys

keys_info = {
    'testnet': {
        'validators': [is_binary],
        'description': 'Run on the test network instead of the real bitcoin network. (Expected value: 0 or 1)'
    },
    'regnet': {
        'validators': [is_binary],
        'description': 'Run a regression test network. (Expected value: 0 or 1)'
    },
    'proxy': {
        'validators': [is_address_with_port],
        'description': 'Connect via a SOCKS5 proxy. (Expected value: address:port)'
    },
    'bind': {
        'validators': [is_address_with_port],
        'description': 'Bind to given address and always listen on it. Use [host]:port notation for IPv6. '
                       '(Expected value: address:port)'
    },
    'whitebind': {
        'validators': [is_address_with_port],
        'description': 'Bind to given address and whitelist peers connecting to it. '
                       'Use [host]:port notation for IPv6. (Expected value: address:port)'
    },
    'addnode': {
        'validators': [is_address],
        'description': 'Use as many addnode= settings as you like to connect to specific peers. '
                       '(Expected value: address:port / address)'
    },
    'connect': {
        'validators': [is_address],
        'description': 'Use as many connect= settings as you like to connect ONLY to specific peers. '
                       '(Expected value: address:port / address)'
    },
    'listen': {
        'validators': [is_binary],
        'description': 'Listening mode, enabled by default except when \'connect\' is being used.'
                       '(Expected value: 0 or 1)'
    },
    'port': {
        'validators': [is_port],
        'description': 'Port on which to listen for connections (default: 8333, testnet: 18333, regtest: 18444).'
                       '(Expected value: 1 to 65535)'
    },
    'maxconnections=': {
        'validators': [is_positive_integer],
        'description': 'Maximum number of inbound+outbound connections. (Expected value: >0)'
    },
    'server': {
        'validators': [is_binary],
        'description': 'server=1 tells Bitcoin-Qt and bitcoind to accept JSON-RPC commands.'
                       '(Expected value: 0 or 1)'
    },
    'rpcbind': {
        'validators': [is_address_with_port],
        'description': 'Bind to given address to listen for JSON-RPC connections. '
                       'Use [host]:port notation for IPv6. This option can be specified multiple times '
                       '(default: bind to all interfaces). (Expected value: address:port)'
    },
    'rpcuser': {
        'validators': [is_non_empty],
        'description': 'RPC user. (Expected value: non-empty)'
    },
    'rpcpassword': {
        'validators': [is_non_empty],
        'description': 'RPC password. (Expected value: non-empty)'
    },
    'rpcauth': {
        'validators': [is_user_and_pass],
        'description': 'This is a unified option for rpcuser:rpcpass. '
                       'You can add multiple entries of these to the server conf file, '
                       'and client can use any of them. (Expected value: non-empty:non-empty)'
    },
    'rpcclienttimeout': {
        'validators': [is_positive_integer],
        'description': 'How many seconds bitcoin will wait for a complete RPC HTTP request after the HTTP '
                       'connection is established. (Expected value: > 0)'
    },
    'rpcallowip': {
        'validators': [is_ip_or_subnet],
        'description': ''
    },
    'rpcport': {
        'validators': [is_port],
        'description': 'Listen for RPC connections on this TCP port. (Expected value: 1 to 65535)'
    },
    'rpcconnect': {
        'validators': [is_address],
        'description': 'You can use Bitcoin or bitcoind to send commands to Bitcoin/bitcoind '
                       'running on another host using this option. (Expected value: address:port / address)'
    },
    'wallet': {
        'validators': [is_folder_path],
        'description': 'Specify where to find wallet, lockfile and logs. If not present, '
                       'those files will be created as new. (Expected value: folder_path)'
    },
    'txconfirmtarget': {
        'validators': [is_positive_integer],
        'description': 'Create transactions that have enough fees so they are likely to begin confirmation '
                       'within n blocks (default: 6). This setting is over-ridden by the -paytxfee option. '
                       '(Expected value: > 0)'
    },
    'paytxfee': {
        'validators': [is_ratio],
        'description': 'Pay a transaction fee every time you send bitcoins. (Expected value: ratio, like 0.01x)'
    },
    'keypool': {
        'validators': [is_positive_integer],
        'description': 'Pre-generate this many public/private key pairs, so wallet backups will be valid for '
                       'both prior transactions and several dozen future transactions. '
                       '(Expected value: > 0)'
    },
    'prune': {
        'validators': [is_non_negative_integer],
        'description': 'Enable pruning to reduce storage requirements by deleting old blocks. '
                       '0 = default (no pruning). '
                       '1 = allows manual pruning via RPC. >=550 = target to stay under in MiB. '
                       '(Expected value: >= 0)'
    },
    'min': {
        'validators': [is_binary],
        'description': ''
    },
    'minimizetotray': {
        'validators': [is_binary],
        'description': ''
    },
    'datadir': {
        'validators': [is_folder_path],
        'description': 'Data directory. (Expected value: folder path)'
    },
    'txindex': {
        'validators': [],
        'description': 'Maintain a full transaction index, used by the getrawtransaction rpc call '
                       '(default: 0). (Expected value: >= 0)'
    },
    'disablewallet': {
        'validators': [is_binary],
        'description': 'Do not load the wallet and disable wallet RPC calls. (Expected value: 0 or 1)'
    },
    'timeout': {
        'validators': [is_positive_integer],
        'description': 'Specify connection timeout in milliseconds (default: 5000). (Expected value: > 0)'
    },
    'dbcache': {
        'validators': [partial(is_integer_in_range, 4, 16385)],
        'description': 'Set database cache size in megabytes (default: 300). (Expected value: 4 to 16384)'
    },
    'zmqpubrawblock': {
        'validators': [is_tcp_address_with_port],
        'description': 'Enable publish raw block in <address>. (Expected value: tcp://address:port)'
    },
    'zmqpubrawtx': {
        'validators': [is_tcp_address_with_port],
        'description': 'Enable publish raw block in <address>. (Expected value: tcp://address:port)'
    },
    'debug': {
        'validators': [is_non_empty],
        'description': 'Output debugging information (default: 0, supplying <category> is optional). '
                       'If <category> is not supplied or if <category> = 1, output all debugging information. '
                       '<category> can be: addrman, alert, bench, cmpctblock, coindb, db, http, libevent, lock, '
                       'mempool, mempoolrej, net, proxy, prune, rand, reindex, rpc, selectcoins, tor, zmq, qt.'
    },
    'discover': {
        'validators': [is_binary],
        'description': 'Discover own IP addresses (default: 1 when listening and no -externalip or -proxy) '
                       '(Expected value: 0 or 1)'
    },
    'maxmempool': {
        'validators': [is_positive_integer],
        'description': 'Keep the transaction memory pool below <n> megabytes (default: 300) (Expected value: > 0)'
    },
    'mempoolexpiry': {
        'validators': [is_positive_integer],
        'description': 'Do not keep transactions in the mempool longer than <n> hours (default: 336) '
                       '(Expected value: > 0)'
    }
}