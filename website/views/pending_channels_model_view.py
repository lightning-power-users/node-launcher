from flask_admin import expose
from flask_admin.model import BaseModelView
# noinspection PyPackageRequirements
from google.protobuf.json_format import MessageToDict
from wtforms import Form

from node_launcher.node_set import NodeSet
from website.constants import network
from website.extensions import cache
from website.formatters.common import satoshi_formatter
from website.formatters.lnd import pub_key_formatter, tx_hash_formatter, \
    channel_point_formatter
from website.models.pending_channel import PendingChannels


class PendingChannelsModelView(BaseModelView):
    column_sortable_list = []
    can_create = False
    can_delete = False
    can_edit = False
    can_view_details = False
    column_display_actions = False

    column_formatters = {
        'capacity': satoshi_formatter,
        'channel_point': channel_point_formatter,
        'closing_txid': tx_hash_formatter,
        'commit_fee': satoshi_formatter,
        'fee_per_kw': satoshi_formatter,
        'limbo_balance': satoshi_formatter,
        'local_balance': satoshi_formatter,
    }
    column_exclude_list = [
        'channel_point',
        'closing_txid',
        'commit_fee',
        'commit_weight',
        'fee_per_kw',
        'limbo_balance',
        'local_balance',
    ]
    column_list = [
        'remote_node_pub',
        'capacity'
    ]

    column_labels = {
        'pending_type': 'Status',
        'remote_node_pub': 'Remote Public Key'
    }

    def get_pk_value(self, model):
        pass

    def scaffold_list_columns(self):
        return [
            'capacity',
            'channel_point',
            'closing_txid',
            'commit_fee',
            'commit_weight',
            'fee_per_kw',
            'limbo_balance',
            'local_balance',
            'pending_type',
            'remote_node_pub',
        ]

    def scaffold_sortable_columns(self):
        pass

    def scaffold_form(self):
        class NewForm(Form):
            pass

        return NewForm

    def scaffold_list_form(self, widget=None, validators=None):
        pass

    def get_list(self, page, sort_field, sort_desc, search, filters,
                 page_size=None):
        node_set = NodeSet(network)
        try:
            response = node_set.lnd_client.list_pending_channels()
            pending_channels = []
            pending_types = [
                'pending_open_channels',
                'pending_closing_channels',
                'pending_force_closing_channels',
                'waiting_close_channels'
            ]
            for pending_type in pending_types:
                for pending_channel in getattr(response, pending_type):
                    channel_dict = MessageToDict(pending_channel)
                    nested_data = channel_dict.pop('channel')
                    # noinspection PyDictCreation
                    flat_dict = {**channel_dict, **nested_data}
                    flat_dict['pending_type'] = pending_type
                    pending_channel_model = PendingChannels(**flat_dict)
                    pending_channels.append(pending_channel_model)
        except Exception as e:
            # todo add error handling
            # todo add error logging
            print(e)
            pending_channels = []
        return len(pending_channels), pending_channels

    # noinspection PyShadowingBuiltins
    def get_one(self, id):
        pass

    def create_model(self, form):
        pass

    def update_model(self, form, model):
        pass

    def delete_model(self, model):
        pass

    def _create_ajax_loader(self, name, options):
        pass

    @expose('/')
    @cache.memoize(300)
    def index_view(self):
        return super(PendingChannelsModelView, self).index_view()
