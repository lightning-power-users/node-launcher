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


@dataclass
class Partition(object):
    mountpoint: str
    gb_free: int


class HardDrives(object):
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
        should_prune = free_gb < AUTOPRUNE_GB
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
