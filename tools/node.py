from datetime import datetime
from typing import List, Optional

from google.protobuf.json_format import MessageToDict
# noinspection PyProtectedMember
from grpc._channel import _Rendezvous

from tools.channel import Channel
from tools.lnd_client import lnd_client


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
            print(details)
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
