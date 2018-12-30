import math
from datetime import datetime
import os
from collections import defaultdict
import time
from typing import List, Optional, Dict

from google.protobuf.json_format import MessageToDict
# noinspection PyProtectedMember
from grpc._channel import _Rendezvous

from node_launcher.node_set.lnd_client import LndClient
from node_launcher.node_set.lnd_client.rpc_pb2 import NodeAddress, \
    OpenStatusUpdate
from tools.exceptions import OutOfFundsException

network = 'mainnet'
class_file_path = os.path.realpath(__file__)
tools_directory_path = os.path.abspath(
    os.path.join(class_file_path,
                 os.path.pardir))
remote_host_path = os.path.join(tools_directory_path, 'remote')
if not os.path.exists(remote_host_path):
    os.mkdir(remote_host_path)
macaroons_path = os.path.join(remote_host_path,
                              'macaroons')
if not os.path.exists(macaroons_path):
    os.mkdir(macaroons_path)

lnd_client = LndClient(lnddir=remote_host_path,
                            grpc_host='localhost',
                            grpc_port=10009,
                            macaroon_path=macaroons_path)


class Channel(object):
    def __init__(self, capacity: int,
                 commit_fee: int,
                 local_balance: int = 0, remote_balance: int = 0,
                 remote_pubkey: str = None, chan_id: int = None,
                 **kwargs):
        self.data = kwargs
        self.remote_pubkey = remote_pubkey
        if not remote_pubkey:
            self.remote_pubkey = kwargs['remote_node_pub']
        if chan_id is not None:
            self.chan_id = int(chan_id)
        else:
            self.chan_id = None
        self.capacity = int(capacity)
        self.local_balance = int(local_balance)
        self.remote_balance = int(remote_balance)
        self.commit_fee = int(commit_fee)

    @property
    def available_capacity(self) -> int:
        return self.capacity - self.commit_fee

    @property
    def balance(self) -> int:
        return int((self.local_balance / self.available_capacity) * 100)

    @property
    def is_mine(self) -> bool:
        return self.balance > 80

    @property
    def is_yours(self) -> bool:
        return self.balance < 20

    @property
    def is_pending(self) -> bool:
        return self.chan_id is None


class MyDefaultDict(defaultdict):
    def __missing__(self, key):
        self[key] = new = self.default_factory(key)
        return new


class Node(object):
    info: dict
    peer_info: dict
    channels: List[Channel]

    def __init__(self, pubkey: str):
        self.pubkey = pubkey
        self.channels = []
        try:
            self.info = MessageToDict(lnd_client.get_node_info(pubkey))
        except _Rendezvous as e:
            if e.details() == 'unable to find node':
                pass
            else:
                raise
        self.peer_info = None

    def add_channel(self, channel: Channel):
        if not [c for c in self.channels if c.chan_id == channel.chan_id]:
            self.channels.append(channel)

    @property
    def last_update(self):
        return datetime.fromtimestamp(self.info['node']['last_update'])

    @property
    def local_balance(self) -> int:
        return sum([c.local_balance for c in self.channels])

    @property
    def remote_balance(self) -> int:
        return sum([c.remote_balance for c in self.channels])

    @property
    def available_capacity(self) -> int:
        return sum([c.available_capacity for c in self.channels])

    @property
    def balance(self) -> Optional[int]:
        if self.available_capacity == 0:
            return None
        return int((self.local_balance / self.available_capacity) * 100)

    @property
    def pending(self) -> int:
        return len([c for c in self.channels if c.is_pending])


class ChannelBalancer(object):
    nodes: Dict[str, Node]

    def __init__(self):
        self.nodes = MyDefaultDict(Node)

    def get_channels(self):
        self.nodes.clear()
        channels = lnd_client.list_channels()
        pending_open_channels = [c for c in lnd_client.list_pending_channels()
                            if c['pending_type'] == 'pending_open_channels']
        [self.nodes[m.remote_pubkey].add_channel(Channel(**MessageToDict(m)))
         for m in channels]
        [self.nodes[m.remote_node_pub].add_channel(Channel(**m))
         for m in pending_open_channels]

    def reconnect(self):
        for node in self.nodes.values():
            print(node.last_update)
            for address in node.info['node']['addresses']:
                print(address['addr'])
                try:
                    lnd_client.connect_peer(node.pubkey, address['addr'])
                except Exception as e:
                    print(e)

    def rebalance(self):
        peers = lnd_client.list_peers()
        total_rebalance = 0
        for peer in peers:
            data = MessageToDict(peer)
            node = self.nodes[data['pub_key']]
            node.peer_info = data
        for node in self.nodes.values():
            if node.peer_info is None or node.balance is None:
                continue
            sat_recv = node.peer_info.get('sat_recv')
            sat_sent = node.peer_info.get('sat_sent')
            if not sat_recv or sat_sent:
                continue

            rebalance_amount = node.remote_balance - node.local_balance
            rebalance_amount = min(max(int(math.ceil(rebalance_amount / 100000.0)) * 100000 * 2, 500000), 16000000)
            if node.balance < 50:
                if rebalance_amount > 100000:
                    total_rebalance += rebalance_amount
                    print(node.pubkey, f'{rebalance_amount:,d}', node.peer_info.get('sat_recv'), node.peer_info.get('sat_sent'))
                    response = lnd_client.open_channel(node_pubkey_string=node.pubkey, local_funding_amount=rebalance_amount, push_sat=0, sat_per_byte=5)
                    try:
                        for update in response:
                            if isinstance(update, OpenStatusUpdate):
                                break
                            else:
                                print(update)
                    except _Rendezvous as e:
                        print(datetime.now(), e)
                        if 'not enough witness outputs to create funding transaction' in e.details():
                            continue
        print(f'{total_rebalance:,d}')

    def identify_dupes(self):
        for pubkey in self.nodes:
            node = self.nodes[pubkey]
            if len(node.channels) < 3:
                continue
            print(node)


if __name__ == '__main__':

    channel_balancer = ChannelBalancer()
    channel_balancer.get_channels()
    # channel_balancer.identify_dupes()
    while True:
        time.sleep(1)
        try:
            channel_balancer.rebalance()
        except OutOfFundsException:
            continue
