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
    OPERATING_SYSTEM, MAXIMUM_GB
)
from node_launcher.app_logging import log


@dataclass
class Partition(object):
    mount_point: str
    capacity_gb: int
    free_gb_incl_bitcoin_dir: int
    has_bitcoin_dir: bool
    bitcoin_dir_size: int
    has_error: bool
    can_archive: bool
    can_full_node: bool
    is_default_partition: bool
    bitcoin_dir_path: Optional[str]


class HardDrives(object):

    @staticmethod
    def is_default_partition(path: str):
        default_partition = os.path.join(BITCOIN_DATA_PATH[OPERATING_SYSTEM], os.pardir)
        default_partition = Path(default_partition).drive
        partition = Path(path).drive
        return default_partition == partition

    @staticmethod
    def get_dir_size(start_path: str) -> int:
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

    def analyze_partition(self, path: str) -> Partition:
        has_bitcoin_dir = False
        is_default_partition = False
        bitcoin_dir_size = 0
        try:
            psutil_disk_usage = psutil.disk_usage(path)
            log.debug('psutil_disk_usage', path=path, psutil_disk_usage=psutil_disk_usage)
        except:
            log.warning(
                'analyze_partition',
                path=path,
                exc_info=True
            )
            return Partition(mount_point=path, free_gb_incl_bitcoin_dir=0, capacity_gb=0, has_bitcoin_dir=False,
                             has_error=True, bitcoin_dir_size=bitcoin_dir_size,
                             is_default_partition=is_default_partition, can_full_node=False, can_archive=False, bitcoin_dir_path=None)

        capacity, used, free, percent = [math.floor(n / GIGABYTE) for n in psutil_disk_usage]
        free_incl_bitcoin_dir = free

        is_default_partition = self.is_default_partition(path)
        if is_default_partition:
            bitcoin_dir_path = BITCOIN_DATA_PATH[OPERATING_SYSTEM]
        else:
            bitcoin_dir_path = os.path.join(path, 'Bitcoin')
        if os.path.exists(bitcoin_dir_path):
            bitcoin_dir_size = self.get_dir_size(bitcoin_dir_path)
            log.info('has bitcoin directory',
                     datadir=bitcoin_dir_path,
                     bitcoin_dir_size=bitcoin_dir_size,
                     is_default_partition=is_default_partition)
            free_incl_bitcoin_dir += bitcoin_dir_size
            has_bitcoin_dir = True

        can_full_node = free_incl_bitcoin_dir > MINIMUM_GB
        can_archive = free_incl_bitcoin_dir < MAXIMUM_GB
        return Partition(mount_point=path, free_gb_incl_bitcoin_dir=free_incl_bitcoin_dir,
                         has_bitcoin_dir=has_bitcoin_dir, has_error=False,
                         capacity_gb=capacity, bitcoin_dir_size=bitcoin_dir_size, can_full_node=can_full_node,
                         can_archive=can_archive,
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
        partition_paths = [
            p.mountpoint for p in ps
            if 'removable' not in p.opts
               and not p.mountpoint.startswith('/System/Volumes')
        ]
        log.info(
            'partition_paths',
            partition_paths=partition_paths
        )
        for path in partition_paths:
            partition = self.analyze_partition(path)
            log.debug('analyze_partition', path=path, partition=partition)
            partitions.append(partition)
        return partitions

    def get_full_node_partition(self) -> Optional[Partition]:
        partitions = self.list_partitions()
        for partition in partitions:
            log.debug('get_full_node_partition', partition=partition)
            if partition.can_full_node and partition.has_bitcoin_dir:
                return partition
            elif partition.can_full_node and partition.is_default_partition:
                return partition
            elif partition.can_full_node:
                return partition
            else:
                continue
        return None
