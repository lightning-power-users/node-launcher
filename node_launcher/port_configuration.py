import errno
import socket


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                return True
            raise
        return False


def get_port(starting_port: int):
    port = starting_port
    while port <= 65535:
        if not is_port_in_use(port):
            return port
        port += 1


def get_zmq_port():
    return get_port(18500)


class PortConfiguration(object):
    def __init__(self):
        self.zmq_block_port = get_zmq_port()
        self.zmq_tx_port = get_zmq_port()
        self.rest_port = get_port(8080)
        self.node_port = get_port(9735)
        self.grpc_port = get_port(10009)
