import json
import os
from datetime import datetime, date
from time import struct_time, mktime
import decimal

from bitcoin.core import COIN
from bitcoin.rpc import Proxy

from node_launcher.logging import log
from node_launcher.node_set import NodeSet
from website.utilities.cache_directory import get_directory, dump_json


def output_fee_estimates():
    node_set = NodeSet()
    proxy = Proxy(btc_conf_file=node_set.bitcoin.file.path)
    fee_estimates = dict(
        ten_minutes=dict(conf_target=1),
        one_hour=dict(conf_target=6),
        six_hours=dict(conf_target=36),
        twelve_hours=dict(conf_target=72),
        one_day=dict(conf_target=144),
        two_days=dict(conf_target=288),
        three_days=dict(conf_target=432),
        one_week=dict(conf_target=1008)
    )

    for key in fee_estimates.keys():
        # noinspection PyProtectedMember
        fee_estimates[key]['conservative'] = proxy._call(
            'estimatesmartfee',
            fee_estimates[key]['conf_target'],
            'CONSERVATIVE'
        )

        # noinspection PyProtectedMember
        fee_estimates[key]['economical'] = proxy._call(
            'estimatesmartfee',
            fee_estimates[key]['conf_target'],
            'ECONOMICAL'
        )

        log.info(
            'estimatesmartfee',
            fee_estimate=fee_estimates[key],
        )

    today = datetime.now()
    dump_json(data=fee_estimates, name='fee_estimate', date=today)


if __name__ == '__main__':
    output_fee_estimates()
