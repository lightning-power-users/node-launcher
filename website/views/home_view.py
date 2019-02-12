import json
import os
from datetime import datetime
from pprint import pformat

import humanize
from flask import render_template
from flask_admin import BaseView, expose
# noinspection PyPackageRequirements
from google.protobuf.json_format import MessageToDict

from node_launcher.node_set import NodeSet
from website.constants import CACHE_PATH
from website.extensions import cache


class HomeView(BaseView):
    @expose('/')
    @cache.memoize(timeout=600)
    def index(self):

        # noinspection PyBroadException
        info_cache_file = os.path.join(CACHE_PATH, 'info.json')
        try:
            node_set = NodeSet()
            info = MessageToDict(node_set.lnd_client.get_info())
            best_header_timestamp = int(info['best_header_timestamp'])
            best_header_datetime = datetime.fromtimestamp(best_header_timestamp)
            best_header_strftime = best_header_datetime.strftime('%c')
            best_header_humanized = humanize.naturaltime(best_header_datetime)

            info['best_header_timestamp'] = f'{best_header_strftime} ({best_header_humanized})'
            with open(info_cache_file, 'w') as f:
                json.dump(info, f)
        except Exception as e:
            raise
            # Todo add logging
            print(pformat(e))
            try:
                with open(info_cache_file, 'r') as f:
                    info = json.load(f)
            except FileNotFoundError:
                info = {}

        return render_template('index.html', info=info)
