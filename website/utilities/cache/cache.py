import json
import os
from datetime import datetime
from pprint import pformat

from node_launcher.logging import log
from website.utilities.cache.fee_estimation import cache_fee_estimate
from website.utilities.cache.fiat_price import cache_usd_price
from website.utilities.cache.get_cache_directory_by_date import (
    get_cache_directory_by_date
)


def get_latest(name, date_time=None):
    if date_time is None:
        date_time = datetime.today()
    directory = get_cache_directory_by_date(date_time)
    files = [f for f in os.listdir(directory) if name in f]
    try:
        latest = max([f.split('-')[1].split('.')[0] for f in files])
    except ValueError:
        latest = 25
    if int(latest) != date_time.hour:
        if name == 'usd_price':
            cache_usd_price()
        elif name == 'fee_estimate':
            cache_fee_estimate()
        else:
            log.error('Cache not implemented', name=name)
        latest = date_time.hour
    file_path = os.path.join(directory, f'{name}-{latest}.json')
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def get_data(name, label):
    directory = get_cache_directory_by_date(date_time)
    file_path = os.path.join(directory, f'{name}-{latest}.json')
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data



if __name__ == '__main__':
    price = get_latest('usd_price')
    fee_estimate = get_latest('fee_estimate')
    print(pformat(price))
    print(pformat(fee_estimate))
