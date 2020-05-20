from typing import Optional

from node_launcher.constants import OPERATING_SYSTEM
from .bitcoind.bitcoind_node import BitcoindNode
from .lib.hard_drives import Partition
from .lib.node_status import NodeStatus
from .lnd.lnd_node import LndNode
from .tor.tor_node import TorNode
from node_launcher.logging import log


class RemoteNodeSet(object):
    tor_node: TorNode
    bitcoind_node: Optional[BitcoindNode]
    lnd_node: LndNode

    def __init__(self):
