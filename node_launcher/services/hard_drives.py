import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

import psutil as psutil

from node_launcher.constants import GIGABYTE, BITCOIN_DATA_PATH, OPERATING_SYSTEM
from node_launcher.utilities import get_dir_size


@dataclass
class Partition(object):
    mountpoint: str
    gb_free: int


class HardDrives(object):
    partitions: List[Partition]

    def __init__(self):
        self.partitions = self.list_partitions()

    @staticmethod
    def get_gb(path: str) -> int:
        try:
            capacity, used, free, percent = psutil.disk_usage(path)
        except (PermissionError, OSError):
            return 0
        free_gb = math.floor(free / GIGABYTE)
        return free_gb

    def list_partitions(self) -> List[Partition]:
        ps = psutil.disk_partitions()
        partition_paths = [p.mountpoint for p in ps if 'removable' not in p.opts]
        partitions = []
        for path in partition_paths:
            free_gb = self.get_gb(path)
            partitions.append(Partition(path, free_gb), )
        return partitions

    def get_big_drive(self) -> Partition:
        max_free_space = max([p.gb_free for p in self.partitions])
        for partition in self.partitions:
            if partition.gb_free == max_free_space:
                return partition

    @staticmethod
    def is_default_partition(partition: Partition):
        default_partition = os.path.join(BITCOIN_DATA_PATH[OPERATING_SYSTEM], os.pardir)
        default_partition = Path(default_partition).drive
        partition = Path(partition.mountpoint).drive
        return default_partition == partition

    @staticmethod
    def should_prune(directory: str, has_bitcoin: bool) -> bool:
        _, _, free_bytes, _ = psutil.disk_usage(os.path.realpath(directory))
        if has_bitcoin:
            bitcoin_bytes = get_dir_size(directory)
            free_bytes += bitcoin_bytes
        else:
            bitcoin_bytes = 0
        free_gb = math.floor(free_bytes / GIGABYTE)
        bitcoin_gb = math.ceil(bitcoin_bytes / GIGABYTE)
        free_gb += bitcoin_gb
        return free_gb < 150
