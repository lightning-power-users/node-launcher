from collections import defaultdict

from google.protobuf.json_format import MessageToDict

from node_launcher.node_set import NodeSet

network = 'mainnet'


class Node(object):
    def __init__(self, pubkey: str):
        self.pubkey = pubkey
        self.channels = []


class Channel(object):
    def __init__(self, chan_id: int, capacity: int, local_balance: int,
                 remote_balance: int, commit_fee: int, **kwargs):
        self.chan_id = int(chan_id)
        self.capacity = int(capacity)
        self.local_balance = int(local_balance)
        self.remote_balance = int(remote_balance)
        self.commit_fee = int(commit_fee)
        print('here')

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


class mydefaultdict(defaultdict):
    def __missing__(self, key):
        self[key] = new = self.default_factory(key)
        return new


class Reciprocator(object):
    def __init__(self):
        self.nodes = mydefaultdict(Node)

    def get_channels(self):

        node_set = NodeSet(network)
        channels = node_set.lnd_client.list_channels()
        for channel in channels:

            self.nodes = [Channel(**MessageToDict(m)) for m in channels]


if __name__ == '__main__':
    reciprocator = Reciprocator()
    reciprocator.get_channels()
    print('here')
