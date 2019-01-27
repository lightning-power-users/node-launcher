import csv
import time
from typing import List

from google.protobuf.json_format import MessageToDict

from node_launcher.node_set.lnd_client.rpc_pb2 import ChannelGraph
from tools.node_operator import lnd_client


def save_to_csv(name: str, data: List[dict]):
    timestamp = time.time()
    with open(f'{name}-{timestamp}.csv', 'w') as f:
        w = csv.DictWriter(f, data[0].keys())
        w.writeheader()
        for d in data:
            w.writerow(d)


def convert_to_dict(data):
    data = [MessageToDict(d) for d in data]
    return data


def extract_data():
    graph: ChannelGraph = lnd_client.get_graph()
    nodes = convert_to_dict(graph.nodes)
    edges = convert_to_dict(graph.edges)
    save_to_csv(name='nodes', data=nodes)
    save_to_csv(name='edges', data=edges)


if __name__ == '__main__':
    extract_data()
