import math
from datetime import datetime

# noinspection PyProtectedMember
from grpc._channel import _Rendezvous

from node_launcher.node_set.lnd_client.rpc_pb2 import OpenStatusUpdate
from tools.lnd_client import lnd_client


def rebalance(self):
    total_rebalance = 0
    for node in self.nodes.values():
        if node.peer_info is None or node.balance is None:
            continue
        sat_recv = node.peer_info.get('sat_recv')
        sat_sent = node.peer_info.get('sat_sent')
        if not sat_recv or sat_sent:
            continue

        rebalance_amount = node.remote_balance - node.local_balance
        rebalance_amount = min(
            max(int(math.ceil(rebalance_amount / 100000.0)) * 100000 * 2,
                500000), 16000000)
        if node.balance < 50:
            if rebalance_amount > 100000:
                total_rebalance += rebalance_amount
                print(node.pubkey, f'{rebalance_amount:,d}',
                      node.peer_info.get('sat_recv'),
                      node.peer_info.get('sat_sent'))
                response = lnd_client.open_channel(
                    node_pubkey_string=node.pubkey,
                    local_funding_amount=rebalance_amount, push_sat=0,
                    sat_per_byte=5)
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
