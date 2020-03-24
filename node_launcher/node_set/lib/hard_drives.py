import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

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
    free_gb: int
    has_bitcoin_dir: bool
    bitcoin_dir_size: int
    has_error: bool


class HardDrives(object):
    def analyze_partition(self, path: str) -> Partition:
        has_bitcoin_dir = False
        bitcoin_dir_size = 0
        try:
            capacity, used, free, percent = psutil.disk_usage(path)
        except:
            log.warning(
                'analyze_partition',
                path=path,
                exc_info=True
            )
            return Partition(mount_point=path, free_gb=0, capacity_gb=0, has_bitcoin_dir=False, has_error=True,
                             bitcoin_dir_size=bitcoin_dir_size)

        free_gb = math.floor(free / GIGABYTE)
        capacity_gb = math.floor(capacity / GIGABYTE)

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
        if self.is_default_partition(path):
            default_datadir = BITCOIN_DATA_PATH[OPERATING_SYSTEM]
            if os.path.exists(default_datadir):
                bitcoin_dir_size = self.get_dir_size(default_datadir)
                log.info('default datadir path', default_datadir=default_datadir,
                         bitcoin_dir_size=bitcoin_dir_size)
                free_gb += bitcoin_dir_size
                has_bitcoin_dir = True
        else:
            common_datadir = os.path.join(path, 'Bitcoin')
            if os.path.exists(common_datadir):
                bitcoin_dir_size = self.get_dir_size(common_datadir)
                log.info('common datadir path', common_datadir=common_datadir, bitcoin_dir_size=bitcoin_dir_size)
                free_gb += bitcoin_dir_size
                has_bitcoin_dir = True
        return Partition(mount_point=path, free_gb=free_gb, has_bitcoin_dir=has_bitcoin_dir, has_error=False,
                         capacity_gb=capacity_gb, bitcoin_dir_size=bitcoin_dir_size)

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
    def is_default_partition(path: str):
        default_partition = os.path.join(BITCOIN_DATA_PATH[OPERATING_SYSTEM], os.pardir)
        default_partition = Path(default_partition).drive
        partition = Path(path).drive
        return default_partition == partition

    @staticmethod
    def should_prune(input_directory: str) -> bool:
        directory = os.path.realpath(input_directory)
        try:
            total, used, free, percent = psutil.disk_usage(directory)
        except:
            log.warning(
                'should_prune_disk_usage',
                input_directory=input_directory,
                directory=directory,
                exc_info=True
            )
            return False
        free_gb = math.floor(free / GIGABYTE)
        should_prune = free_gb < MINIMUM_GB
        log.info(
            'should_prune',
            input_directory=input_directory,
            total=total,
            used=used,
            free=free,
            percent=percent,
            free_gb=free_gb,
            should_prune=should_prune
        )
        return should_prune

    def get_dir_size(self, start_path: str) -> int:
        total_size = 0
        entries = None
        try:
            entries = os.scandir(start_path)
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    total_size += self.get_dir_size(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    total_size += entry.stat().st_size
        except:
            log.warning(
                'get_dir_size',
                start_path=start_path,
                total_size=total_size,
                entries=entries,
                exc_info=True
            )
        return total_size
