from flask_admin import expose

from website.extensions import cache
from website.views.lnd_model_view import LNDModelView
from website.formatters.common import satoshi_formatter, format_bool
from website.formatters.lnd import channel_point_formatter


class OpenChannelsModelView(LNDModelView):
    column_sortable_list = []
    can_create = False
    can_delete = False
    can_edit = False
    can_view_details = False
    get_query = 'list_channels'
    primary_key = 'chan_id'

    form_excluded_columns = ['node_pubkey']
    column_exclude_list = [
        'local_balance',
        'remote_balance',
        'commit_fee',
        'commit_weight',
        'unsettled_balance',
        'total_satoshis_received',
        'num_updates',
        'pending_htlcs',
        'csv_delay',
        'private',
        'fee_per_kw',
        'total_satoshis_sent',
        'chan_id',
        'channel_point'
    ]
    column_formatters = {
        'channel_point': channel_point_formatter,
        'capacity': satoshi_formatter,
        'local_balance': satoshi_formatter,
        'remote_balance': satoshi_formatter,
        'commit_fee': satoshi_formatter,
        'fee_per_kw': satoshi_formatter,
        'total_satoshis_sent': satoshi_formatter,
        'total_satoshis_received': satoshi_formatter,
        'unsettled_balance': satoshi_formatter,
        'active': format_bool
    }

    column_labels = {
        'pending_type': 'Status',
        'remote_pubkey': 'Remote Public Key'
    }

    def _create_ajax_loader(self, name, options):
        pass

    @expose('/')
    @cache.memoize(300)
    def index_view(self):
        return super(OpenChannelsModelView, self).index_view()
