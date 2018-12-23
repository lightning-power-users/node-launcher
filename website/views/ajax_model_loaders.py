from flask_admin.model.ajax import AjaxModelLoader, DEFAULT_PAGE_SIZE
from markupsafe import Markup

from website.formatters.lnd import pub_key_formatter
from website.views.lnd_model_view import LNDModelView
from node_launcher.node_set.lnd_client.rpc_pb2 import Channel


class PeersAjaxModelLoader(AjaxModelLoader):
    def __init__(self, name, model, **options):
        super(PeersAjaxModelLoader, self).__init__(name, options)

        self.model = model

    def format(self, model):
        if model is None:
            return '', ''
        formatted = pub_key_formatter(view=None, context=None, model=model, name='pub_key')
        return model.pub_key, Markup(formatted).striptags()

    def get_one(self, pk):
        return [r for r in LNDModelView(Channel).ln.get_peers()
                if r.pub_key == pk][0]

    def get_list(self, query, offset=0, limit=DEFAULT_PAGE_SIZE):
        pub_keys = LNDModelView(Channel).ln.get_peers()
        return pub_keys

