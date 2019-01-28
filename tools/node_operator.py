from collections import defaultdict
from datetime import datetime
from pprint import pformat
from typing import Dict

from google.protobuf.json_format import MessageToDict
# noinspection PyProtectedMember
from grpc._channel import _Rendezvous

from node_launcher.node_set.lnd_client.rpc_pb2 import OpenStatusUpdate
from tools.channel import Channel
from tools.google_sheet import get_google_sheet_data
from tools.lnd_client import lnd_client
from tools.node import Node


class MyDefaultDict(defaultdict):
    def __missing__(self, key):
        self[key] = new = self.default_factory(key)
        return new


class NodeOperator(object):
    nodes: Dict[str, Node]

    def __init__(self):
        self.nodes = MyDefaultDict(Node)
        self.get_channels()
        self.get_peers()

    def get_channels(self):
        channels = lnd_client.list_channels()
        [self.nodes[m.remote_pubkey].add_channel(Channel(**MessageToDict(m)))
         for m in channels]

        pending_channels = [c for c in lnd_client.list_pending_channels()]
        [self.nodes[m.remote_node_pub].add_channel(Channel(**m))
         for m in pending_channels]

        closed_channels = [c for c in lnd_client.closed_channels()]
        [self.nodes[m.remote_pubkey].add_channel(Channel(**MessageToDict((m))))
         for m in closed_channels]

    def get_peers(self):
        peers = lnd_client.list_peers()
        for peer in peers:
            data = MessageToDict(peer)
            node = self.nodes[data['pub_key']]
            node.peer_info = data

    def reconnect(self):
        for node in self.nodes.values():
            if node.info is None or node.peer_info is not None:
                continue
            for address in node.info['node'].get('addresses', []):
                print(node.pubkey, address['addr'])
                try:
                    lnd_client.connect_peer(node.pubkey,
                                            address['addr'],
                                            timeout=5)
                except _Rendezvous as e:
                    print(e.details())

    def close_channels(self, ip_address: str):
        for node in self.nodes.values():
            ip_addresses = []
            if node.info is None:
                continue
            for address in node.info['node'].get('addresses', []):
                ip_addresses.append(address['addr'])
                if ip_address in address['addr']:
                    for channel in node.channels:
                        force = not channel.is_active
                        txid = lnd_client.close_channel(
                            channel_point=channel.channel_point,
                            force=force,
                            sat_per_byte=1
                            )
                        print(pformat(MessageToDict(txid)))
            print(node.pubkey, ip_addresses)
        print(len(self.nodes.values()))

    def identify_dupes(self):
        for pubkey in self.nodes:
            node = self.nodes[pubkey]
            if len(node.channels) < 3:
                continue
            print(node)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='LND Node Operator Tools'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Display additional information for debugging'
    )

    parser.add_argument(
        'action',
        type=str
    )

    parser.add_argument(
        '--ip_address',
        '-i',
        type=str
    )

    args = parser.parse_args()

    node_operator = NodeOperator()

    if args.action == 'close' and args.ip_address:
        node_operator.close_channels(ip_address=args.ip_address)

    elif args.action == 'reconnect':
        node_operator.reconnect()

    elif args.action == 'sheet':
        get_google_sheet_data(node_operator)

    elif args.action == 'open':
        response = lnd_client.open_channel(
            node_pubkey_string=args.pubkey,
            local_funding_amount=args.size,
            push_sat=0,
            sat_per_byte=args.fee,
            spend_unconfirmed=True
        )
        try:
            for update in response:
                if isinstance(update, OpenStatusUpdate):
                    print(update)
                    break
                else:
                    print(update)
        except _Rendezvous as e:
            print(datetime.now(), e)

    elif args.action == 'dupes':
        node_operator.identify_dupes()

