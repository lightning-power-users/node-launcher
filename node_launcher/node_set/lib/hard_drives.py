import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import psutil as psutil

from node_launcher.constants import (
    MINIMUM_GB,
    BITCOIN_DATA_PATH,
    GIGABYTE,
    OPERATING_SYSTEM
)
from node_launcher.logging import log


@dataclass
class Partition(object):
    mount_point: str
    capacity_gb: int
    free_gb_incl_bitcoin_dir: int
    has_bitcoin_dir: bool
    bitcoin_dir_size: int
    has_error: bool
    can_full_node: bool
    is_default_partition: bool
    bitcoin_dir_path: Optional[str]


class HardDrives(object):
    def analyze_partition(self, path: str) -> Partition:
        has_bitcoin_dir = False
        is_default_partition = False
        bitcoin_dir_size = 0
        try:
            capacity, used, free, percent = psutil.disk_usage(path)
        except:
            log.warning(
                'analyze_partition',
                path=path,
                exc_info=True
            )
            return Partition(mount_point=path, free_gb_incl_bitcoin_dir=0, capacity_gb=0, has_bitcoin_dir=False,
                             has_error=True, bitcoin_dir_size=bitcoin_dir_size,
                             is_default_partition=is_default_partition, can_full_node=False, bitcoin_dir_path=None)

        free_gb = math.floor(free / GIGABYTE)
        capacity_gb = math.floor(capacity / GIGABYTE)
        free_gb_incl_bitcoin_dir = free_gb
        log.info(
            'psutil',
            path=path,
            capacity=capacity,
            capacity_gb=capacity_gb,
            used=used,
            free=free,
            percent=percent,
            free_gb=free_gb
        )
        is_default_partition = self.is_default_partition(path)
        if is_default_partition:
            bitcoin_dir_path = BITCOIN_DATA_PATH[OPERATING_SYSTEM]
            if os.path.exists(bitcoin_dir_path):
                bitcoin_dir_size = self.get_dir_size(bitcoin_dir_path)
                log.info('default datadir path', default_datadir=bitcoin_dir_path,
                         bitcoin_dir_size=bitcoin_dir_size)
                free_gb_incl_bitcoin_dir += bitcoin_dir_size
                has_bitcoin_dir = True
        else:
            bitcoin_dir_path = os.path.join(path, 'Bitcoin')
            if os.path.exists(bitcoin_dir_path):
                bitcoin_dir_size = self.get_dir_size(bitcoin_dir_path)
                log.info('common datadir path', common_datadir=bitcoin_dir_path, bitcoin_dir_size=bitcoin_dir_size)
                free_gb_incl_bitcoin_dir += bitcoin_dir_size
                has_bitcoin_dir = True
        can_full_node = free_gb_incl_bitcoin_dir > MINIMUM_GB
        return Partition(mount_point=path, free_gb_incl_bitcoin_dir=free_gb_incl_bitcoin_dir,
                         has_bitcoin_dir=has_bitcoin_dir, has_error=False,
                         capacity_gb=capacity_gb, bitcoin_dir_size=bitcoin_dir_size, can_full_node=can_full_node,
                         is_default_partition=is_default_partition, bitcoin_dir_path=bitcoin_dir_path)

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
            partition = self.analyze_partition(path)
            partitions.append(partition)
        return partitions

    def get_full_node_partition(self) -> Optional[Partition]:
        partitions = self.list_partitions()
        for partition in partitions:
            if partition.can_full_node and partition.has_bitcoin_dir:
                return partition
            elif partition.can_full_node and partition.is_default_partition:
                return partition
            elif partition.can_full_node:
                return partition
            else:
                return None

    @staticmethod
    def is_default_partition(path: str):
        default_partition = os.path.join(BITCOIN_DATA_PATH[OPERATING_SYSTEM], os.pardir)
        default_partition = Path(default_partition).drive
        partition = Path(path).drive
        return default_partition == partition

    def get_dir_size(self, start_path: str) -> int:
        total_size = 0
        entries = None
        try:
            for dirpath, dirnames, filenames in os.walk(start_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    # skip if it is symbolic link
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
        except:
            log.warning(
                'get_dir_size',
                start_path=start_path,
                total_size=total_size,
                entries=entries,
                exc_info=True
            )
        total_size_gb = math.floor(total_size / GIGABYTE)
        return total_size_gb
