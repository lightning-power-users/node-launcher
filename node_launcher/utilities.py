import os
from random import choice
from string import ascii_lowercase, digits


def get_dir_size(start_path: str) -> int:
    total_size = 0
    for entry in os.scandir(start_path):
        if entry.is_dir(follow_symlinks=False):
            total_size += get_dir_size(entry.path)
        elif entry.is_file(follow_symlinks=False):
            total_size += entry.stat().st_size
    return total_size


def get_random_password() -> str:
    return ''.join(choice(ascii_lowercase + digits) for _ in range(30))
