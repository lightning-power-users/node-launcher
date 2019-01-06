import math
import os
import time
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from google.protobuf.json_format import MessageToDict
# noinspection PyProtectedMember
from grpc._channel import _Rendezvous

from node_launcher.node_set.lnd_client import LndClient
from node_launcher.node_set.lnd_client.rpc_pb2 import OpenStatusUpdate
from tools.secrets import spreadsheet_id

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
                 channel_point: str = None,
                 **kwargs):
        self.data = kwargs
        self.remote_pubkey = remote_pubkey
        if not remote_pubkey:
            self.remote_pubkey = kwargs['remote_node_pub']
        self.channel_point = channel_point
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
        self.peer_info = None
        self.info = None
        try:
            self.info = MessageToDict(lnd_client.get_node_info(pubkey))
        except _Rendezvous as e:
            details = e.details().lower()
            if details == 'unable to find node':
                pass
            elif 'invalid byte' in details:
                pass
            else:
                raise

    def add_channel(self, channel: Channel):
        if not [c for c in self.channels if c.chan_id == channel.chan_id]:
            self.channels.append(channel)

    @property
    def last_update(self) -> Optional[datetime]:
        if self.info is not None:
            last_update = self.info['node'].get('last_update')
            if last_update is not None:
                return datetime.fromtimestamp(last_update)
        return None

    @property
    def local_balance(self) -> int:
        return sum([c.local_balance for c in self.channels])

    @property
    def remote_balance(self) -> int:
        return sum([c.remote_balance for c in self.channels])

    @property
    def capacity(self) -> int:
        return sum([c.capacity for c in self.channels])

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
                                 if
                                 c['pending_type'] == 'pending_open_channels']
        [self.nodes[m.remote_pubkey].add_channel(Channel(**MessageToDict(m)))
         for m in channels]
        [self.nodes[m.remote_node_pub].add_channel(Channel(**m))
         for m in pending_open_channels]

    def reconnect(self):
        peers = lnd_client.list_peers()
        for peer in peers:
            data = MessageToDict(peer)
            node = self.nodes[data['pub_key']]
            node.peer_info = data
        for node in self.nodes.values():
            print(node.last_update)
            if node.info is None or node.peer_info is not None:
                continue
            for address in node.info['node'].get('addresses', []):
                print(address['addr'])
                try:
                    lnd_client.connect_peer(node.pubkey, address['addr'])
                except Exception as e:
                    print(e)

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

    def identify_dupes(self):
        for pubkey in self.nodes:
            node = self.nodes[pubkey]
            if len(node.channels) < 3:
                continue
            print(node)

    def get_google_sheet_data(self):
        from googleapiclient.discovery import build
        from httplib2 import Http
        from oauth2client import file, client, tools
        SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

        SAMPLE_RANGE_NAME = 'Form Responses 1!A1:J'
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        store = file.Storage('token.json')
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            credentials = tools.run_flow(flow, store)
        service = build('sheets', 'v4', http=credentials.authorize(Http()))

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
        else:
            total = 0
            for index, row in enumerate(values[1:]):
                old_row = row[3:]
                pubkey = row[1].split('@')[0]
                # twitter_handle = row.get(2)
                if pubkey in self.nodes:
                    node = self.nodes[pubkey]
                    txids = [c.channel_point for c in node.channels]
                    new_row = [
                        len(node.channels),
                        node.remote_balance,
                        node.local_balance,
                        node.available_capacity,
                        node.balance,
                        ', '.join(txids)
                    ]
                    status = ''
                    if len(node.channels) == 1 and node.remote_balance:
                        total += node.capacity
                        print(node.pubkey, "{0:,d}".format(node.capacity))
                        response = lnd_client.open_channel(
                            node_pubkey_string=node.pubkey,
                            local_funding_amount=max(node.capacity, 200000),
                            push_sat=0,
                            sat_per_byte=1,
                            spend_unconfirmed=True
                        )
                        try:
                            for update in response:
                                if isinstance(update, OpenStatusUpdate):
                                    print(update)
                                    status = 'Pending channel'
                                    break
                                else:
                                    print(update)
                        except _Rendezvous as e:
                            status = e.details()
                    new_row.append(status)
                else:
                    new_row = [
                        0,
                        0,
                        0,
                        0,
                        0,
                        ''
                    ]
                changed = False
                for i, _ in enumerate(new_row[:-2]):
                    try:
                        if old_row[i] == '':
                            old_row[i] = 0
                        old_value = int(float(str(old_row[i]).replace(',', '')))
                    except IndexError:
                        old_value = 0

                    if int(new_row[i]) != old_value:
                        changed = True
                        break
                if changed or True:
                    body = dict(values=[new_row])
                    try:
                        result = service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=f'Form Responses 1!D{index+2}:J',
                        body=body,
                        valueInputOption='USER_ENTERED').execute()
                        time.sleep(0.5)
                    except Exception as e:
                        pass


if __name__ == '__main__':
    channel_balancer = ChannelBalancer()
    channel_balancer.get_channels()
    # channel_balancer.reconnect()
    channel_balancer.get_google_sheet_data()

    # response = lnd_client.open_channel(
    #     node_pubkey_string='',
    #     local_funding_amount=,
    #     push_sat=0,
    #     sat_per_byte=1,
    #     spend_unconfirmed=True
    # )
    # try:
    #     for update in response:
    #         if isinstance(update, OpenStatusUpdate):
    #             print(update)
    #             break
    #         else:
    #             print(update)
    # except _Rendezvous as e:
    #     print(datetime.now(), e)

    # channel_balancer.identify_dupes()
    # while True:
    #     time.sleep(1)
    #     try:
    #         channel_balancer.rebalance()
    #     except OutOfFundsException:
    #         continue
