from node_launcher.node_set.lnd_client.rpc_pb2 import Channel as Channels


class DefaultModel(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)


class PendingChannels(DefaultModel):
    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return None
