import errno
import os
import secrets
import socket

from node_launcher.logging import log


def get_dir_size(start_path: str) -> int:
    total_size = 0
    entries = None
    try:
        entries = os.scandir(start_path)
        for entry in entries:
            if entry.is_dir(follow_symlinks=False):
                total_size += get_dir_size(entry.path)
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


def get_random_password() -> str:
    return secrets.token_hex()


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
