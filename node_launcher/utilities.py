import os


def get_dir_size(start_path: str) -> int:
    total_size = 0
    for entry in os.scandir(start_path):
        if entry.is_dir(follow_symlinks=False):
            total_size += get_dir_size(entry.path)
        elif entry.is_file(follow_symlinks=False):
            total_size += entry.stat().st_size
    return total_size
