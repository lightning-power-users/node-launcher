import csv
import time
from typing import List

from google.protobuf.json_format import MessageToDict
import networkx as nx

from node_launcher.node_set.lnd_client.rpc_pb2 import ChannelGraph
from tools.node_operator import lnd_client


def convert_to_dict(data):
    data = [MessageToDict(d) for d in data]
    return data


def save_to_csv(name: str, data: List[dict]):
    timestamp = time.time()
    with open(f'{name}-{timestamp}.csv', 'w') as f:
        w = csv.DictWriter(f, data[0].keys())
        w.writeheader()
        for d in data:
            w.writerow(d)


class LightningGraph(object):
    def __init__(self):
        self.graph: ChannelGraph = lnd_client.get_graph()
        self.nodes = convert_to_dict(self.graph.nodes)
        self.edges = convert_to_dict(self.graph.edges)

    def to_csv(self):
        save_to_csv(name='nodes', data=self.nodes)
        save_to_csv(name='edges', data=self.edges)

    def eigen(self):
        pass


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Interact with the Lightning graph'
    )

    parser.add_argument(
        'action',
        type=str
    )
    args = parser.parse_args()
    lightning_graph = LightningGraph()
    if args.action == 'csv':
        lightning_graph.to_csv()
    elif args.action == 'eigen':
        lightning_graph.eigen()
