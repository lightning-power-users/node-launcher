import os

from node_launcher.node_set import NodeSet
from node_launcher.node_set.lnd_client import LndClient

network = 'mainnet'
class_file_path = os.path.realpath(__file__)
tools_directory_path = os.path.abspath(
    os.path.join(class_file_path,
                 os.path.pardir))
remote_host_path = os.path.join(tools_directory_path, 'remote')
if not os.path.exists(remote_host_path):
    os.mkdir(remote_host_path)
macaroons_path = os.path.join(remote_host_path,
                              'macaroons')
if not os.path.exists(macaroons_path):
    os.mkdir(macaroons_path)

lnd_remote_client = LndClient(
    lnddir=remote_host_path,
    grpc_host='localhost',
    grpc_port=10010,
    macaroon_path=macaroons_path
)


def get_local_client():
    node_set = NodeSet()
    return node_set.lnd_client
