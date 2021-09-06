import sys

from node_launcher.gui.channel_application import ChannelApplication
from node_launcher.node_set.lnd.lnd_client import LndClient

if __name__ == '__main__':
    # sys.excepthook = except_hook

    import argparse

    parser = argparse.ArgumentParser()
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

    app = ChannelApplication(client=lnd_client)
    sys.exit(app.start())
