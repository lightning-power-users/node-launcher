import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

import psutil as psutil

from node_launcher.constants import (
    AUTOPRUNE_GB,
    BITCOIN_DATA_PATH,
    GIGABYTE,
    OPERATING_SYSTEM
)
from node_launcher.logging import log
from node_launcher.utilities.utilities import get_dir_size


@dataclass
class Partition(object):
    mountpoint: str
    gb_free: int


class HardDrives(object):
    partitions: List[Partition]

    @staticmethod
    def get_gb(path: str) -> int:
        try:
            capacity, used, free, percent = psutil.disk_usage(path)
        except:
            log.warning(
                'get_gb',
                path=path,
                exc_info=True
            )
            return 0

        free_gb = math.floor(free / GIGABYTE)
        log.info(
            'get_gb',
            path=path,
            capacity=capacity,
            used=used,
            free=free,
            percent=percent,
            free_gb=free_gb
        )
        return free_gb

    def list_partitions(self) -> List[Partition]:
        partitions = []
        try:
            ps = psutil.disk_partitions()
        except:
            log.warning(
                'list_partitions',
                exc_info=True
            )
            return partitions
        partition_paths = [p.mountpoint for p in ps if 'removable' not in p.opts]
        log.info(
            'partition_paths',
            partition_paths=partition_paths
        )
        for path in partition_paths:
            free_gb = self.get_gb(path)
            partitions.append(Partition(path, free_gb), )
        return partitions

    def get_big_drive(self) -> Partition:
        partitions = self.list_partitions()
        max_free_space = max([p.gb_free for p in partitions])
        for partition in partitions:
            if partition.gb_free == max_free_space:
                log.info(
                    'get_big_drive',
                    partition=partition
                )
                return partition

    @staticmethod
    def is_default_partition(partition: Partition):
        default_partition = os.path.join(BITCOIN_DATA_PATH[OPERATING_SYSTEM], os.pardir)
        default_partition = Path(default_partition).drive
        partition = Path(partition.mountpoint).drive
        return default_partition == partition

    @staticmethod
    def should_prune(input_directory: str, has_bitcoin: bool) -> bool:
        directory = os.path.realpath(input_directory)
        try:
            total, used, free, percent = psutil.disk_usage(os.path.realpath(directory))
        except:
            log.warning(
                'should_prune_disk_usage',
                input_directory=input_directory,
                directory=directory,
                exc_info=True
            )
            return False
        if has_bitcoin:
            bitcoin_bytes = get_dir_size(directory)
            free += bitcoin_bytes
        else:
            bitcoin_bytes = 0
        free_gb = math.floor(free / GIGABYTE)
        bitcoin_gb = math.ceil(bitcoin_bytes / GIGABYTE)
        free_gb += bitcoin_gb
        should_prune = free_gb < AUTOPRUNE_GB
        log.info(
            'should_prune',
            input_directory=input_directory,
            has_bitcoin=has_bitcoin,
            total=total,
            used=used,
            free=free,
            bitcoin_bytes=bitcoin_bytes,
            percent=percent,
            free_gb=free_gb,
            bitcoin_gb=bitcoin_gb,
            should_prune=should_prune
        )
        return should_prune
