import math
from dataclasses import dataclass
from typing import List

import psutil as psutil

from node_launcher.constants import GIGABYTE


@dataclass
class Partition(object):
    mountpoint: str
    gb_free: int


class HardDrives(object):
    partitions: List[Partition]

    def __init__(self):
        self.partitions = self.list_partitions()

    @staticmethod
    def list_partitions() -> List[Partition]:
        partitions = []
        partition_paths = [p.mountpoint for p in psutil.disk_partitions()]
        for path in partition_paths:
            psutil.disk_usage(path)
            _, _, free_bytes, _ = psutil.disk_usage(path)
            free_gb = math.floor(free_bytes / GIGABYTE)
            partitions.append(Partition(path, free_gb), )
        return partitions

    def get_big_drive(self) -> Partition:
        max_free_space = max([p.gb_free for p in self.partitions])
        for partition in self.partitions:
            if partition.gb_free == max_free_space:
                return partition
