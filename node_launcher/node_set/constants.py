from enum import Enum


class BitcoinState(Enum):
    EXTERNAL = 'EXTERNAL'
    EXTERNAL_NO_ZMQ = 'EXTERNAL_NO_ZMQ'
    MERGED = 'MERGED'
