import os
import subprocess
from pathlib import Path
from random import choice
from string import ascii_lowercase, digits

from node_launcher.constants import IS_MACOS, IS_WINDOWS, OPERATING_SYSTEM


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


def reveal(path: str):
    if IS_MACOS:
        contents = os.listdir(path)
        contents.sort()
        if contents:
            path = os.path.join(path, contents[0])
        subprocess.call(['open', '-R', path])
    elif IS_WINDOWS:
        subprocess.call(f'explorer "{Path(path)}"', shell=True)
    else:
        raise NotImplementedError(f'reveal method has not been implemented for {OPERATING_SYSTEM}')
