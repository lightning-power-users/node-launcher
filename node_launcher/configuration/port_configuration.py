import errno
import socket

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


class PortConfiguration(object):
    def __init__(self):
        self.zmq_block = get_zmq_port()
        self.zmq_tx = get_zmq_port()
        self.rest = get_port(8080)
        self.node = get_port(9735)
        self.grpc = get_port(10009)
