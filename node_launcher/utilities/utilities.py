import errno
import os
import socket
from random import choice
from string import ascii_lowercase, digits


def get_dir_size(start_path: str) -> int:
    total_size = 0
    try:
        for entry in os.scandir(start_path):
            if entry.is_dir(follow_symlinks=False):
                total_size += get_dir_size(entry.path)
            elif entry.is_file(follow_symlinks=False):
                total_size += entry.stat().st_size
    except PermissionError:
        pass
    return total_size


def get_random_password() -> str:
    return ''.join(choice(ascii_lowercase + digits) for _ in range(30))


claimed_ports = []


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
        except socket.error as e:
            if e.errno == errno.EADDRINUSE or e.errno == 10013:
                return True
            raise
        return False


def get_port(starting_port: int):
    port = starting_port
    while port <= 65535:
        if port in claimed_ports:
            port += 1
            continue
        if not is_port_in_use(port):
            claimed_ports.append(port)
            return port
        port += 1


def get_zmq_port():
    return get_port(18500)
