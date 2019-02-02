import socket

import requests


def get_local_ip_address():
    return socket.gethostbyname(socket.gethostname())


def get_public_ip_address():
    response = requests.get('http://httpbin.org/ip').json()
    return response['origin']
