from flask_admin import expose

from website.admin.lnd_model_view import LNDModelView
from website.formatters.common import satoshi_formatter
from website.formatters.lnd import channel_point_formatter, pub_key_formatter


class OpenChannelsModelView(LNDModelView):
    can_create = False
    can_delete = False
    can_edit = False
    get_query = 'list_channels'
    primary_key = 'chan_id'

    column_default_sort = 'chan_id'
    form_excluded_columns = ['node_pubkey']
    column_exclude_list = [
        ''
    ]
    column_formatters = {
        'remote_pubkey': pub_key_formatter,
        'channel_point': channel_point_formatter,
        'capacity': satoshi_formatter,
        'local_balance': satoshi_formatter,
        'remote_balance': satoshi_formatter,
        'commit_fee': satoshi_formatter,
        'fee_per_kw': satoshi_formatter,
        'total_satoshis_sent': satoshi_formatter,
        'total_satoshis_received': satoshi_formatter,
        'unsettled_balance': satoshi_formatter,

    }

    def _create_ajax_loader(self, name, options):
        pass

    @expose('/')
    def index_view(self):
        return super(OpenChannelsModelView, self).index_view()
