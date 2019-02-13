from datetime import datetime

from bitcoin.rpc import Proxy

from node_launcher.logging import log
from node_launcher.node_set import NodeSet
from website.utilities.cache_directory import dump_json


def output_fee_estimates():
    node_set = NodeSet()
    proxy = Proxy(btc_conf_file=node_set.bitcoin.file.path)
    fee_estimates = [
        dict(conf_target=1, label='Ten minutes'),
        dict(conf_target=6, label='One_hour'),
        dict(conf_target=36, label='Six hours'),
        dict(conf_target=72, label='Twelve hours'),
        dict(conf_target=144, label='One day'),
        dict(conf_target=288, label='Two days'),
        dict(conf_target=432, label='Three days'),
        dict(conf_target=1008, label='One week')
    ]

    for fee_estimate in fee_estimates:
        # noinspection PyProtectedMember
        fee_estimate['conservative'] = proxy._call(
            'estimatesmartfee',
            fee_estimate['conf_target'],
            'CONSERVATIVE'
        )

        # noinspection PyProtectedMember
        fee_estimate['economical'] = proxy._call(
            'estimatesmartfee',
            fee_estimate['conf_target'],
            'ECONOMICAL'
        )

        log.info(
            'estimatesmartfee',
            fee_estimate=fee_estimate,
        )

    today = datetime.now()
    dump_json(data=fee_estimates, name='fee_estimate', date=today)


if __name__ == '__main__':
    output_fee_estimates()
