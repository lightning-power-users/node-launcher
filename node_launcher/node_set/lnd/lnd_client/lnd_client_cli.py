import os
import sys

from node_launcher.node_set.lnd.lnd_client import LndClient

sys.path.append(os.getcwd())
print(sys.path)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='LND Client CLI'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Display additional information for debugging'
    )

    parser.add_argument(
        '-d',
        type=str,
        help='Path to LND directory'
    )

    parser.add_argument(
        '-host',
        type=str,
        help='gRPC Host'
    )

    parser.add_argument(
        '-port',
        type=str,
        help='gRPC Port'
    )

    parser.add_argument(
        'action',
        type=str
    )
    args = parser.parse_args()
    lnd_client = LndClient(lnddir=args.d,
                           grpc_host=args.host,
                           grpc_port=args.port)

    if args.action == 'balances':
        balances = lnd_client.get_lnd_balances()
        print(balances)
