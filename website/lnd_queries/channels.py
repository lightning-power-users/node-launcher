from google.protobuf.json_format import MessageToDict

from node_launcher.logging import log
from tools.lnd_client import lnd_remote_client
from website.extensions import cache


@cache.cached(timeout=3600, key_prefix='list_open_channels')
def list_open_channels():
    r = [MessageToDict(c) for c in lnd_remote_client.list_channels()]
    return r


@cache.cached(timeout=3600, key_prefix='list_pending_channels')
def list_pending_channels():
    r = [dict(c) for c in lnd_remote_client.list_pending_channels()]
    return r


@cache.cached(timeout=3600, key_prefix='list_closed_channels')
def list_closed_channels():
    r = [MessageToDict(c) for c in lnd_remote_client.closed_channels()]
    return r


def get_open_channels(pubkey: str = None):
    open_channels = list_open_channels()
    if pubkey:
        open_channels = [c for c in open_channels if
                         c['remote_pubkey'] == pubkey]
    log.debug(
        'get_open_channels',
        pubkey=pubkey,
        open_channels=len(open_channels)
    )
    return open_channels


def get_pending_channels(pubkey: str = None):
    pending_channels = list_pending_channels()
    if pubkey:
        pending_channels = [c for c in pending_channels if
                            c['remote_node_pub'] == pubkey]
    log.debug(
        'get_pending_channels',
        pubkey=pubkey,
        pending_channels=len(pending_channels)
    )
    return pending_channels


def get_closed_channels(pubkey: str = None):
    closed_channels = list_closed_channels()
    if pubkey:
        closed_channels = [c for c in closed_channels if
                           c['remote_pubkey'] == pubkey]
    log.debug(
        'get_closed_channels',
        pubkey=pubkey,
        closed_channels=len(closed_channels)
    )
    return closed_channels


class Channels(object):
    def __init__(self, pubkey: str = None):
        self.open_channels = get_open_channels(pubkey)
        self.pending_channels = get_pending_channels(pubkey)
        self.closed_channels = get_closed_channels(pubkey)

    def __len__(self):
        return len(self.open_channels) + len(self.closed_channels)

    @property
    def local_balance(self) -> int:
        local_balance = sum([int(c['local_balance']) for c in self.open_channels])
        local_balance += sum([int(c['local_balance']) for c in self.pending_channels])
        return local_balance

    @property
    def remote_balance(self) -> int:
        remote_balance = sum([int(c['remote_balance']) for c in self.open_channels])
        remote_balance += sum([int(c['remote_balance']) for c in self.pending_channels])
        return remote_balance

    @property
    def net_remote_balance(self) -> int:
        return self.remote_balance - self.local_balance


if __name__ == '__main__':
    get_open_channels()
