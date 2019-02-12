import hashlib
import hmac
import json
import os
import time
from datetime import datetime

import requests

from website.constants import CACHE_PATH


class BitcoinAverage(object):
    base_url = 'https://apiv2.bitcoinaverage.com'

    @property
    def signature(self):
        secret_key = os.environ['BITCOIN_AVERAGE_SECRET_KEY']
        encoded_secret_key = secret_key.encode()

        public_key = os.environ['BITCOIN_AVERAGE_PUBLIC_KEY']

        timestamp = int(time.time())

        payload = f'{timestamp}.{public_key}'
        encoded_payload = payload.encode()

        digest_module = hashlib.sha256

        hashing_object = hmac.new(key=encoded_secret_key,
                                  msg=encoded_payload,
                                  digestmod=digest_module)
        hex_hash = hashing_object.hexdigest()

        return f'{payload}.{hex_hash}'

    def get_price_by_date(self, date: datetime):
        timestamp = int(date.timestamp())
        return self.get_price(timestamp=timestamp)

    def get_price(self, timestamp: int):
        path = [self.base_url, 'indices', 'global', 'history', 'BTCUSD']
        url = '/'.join(path)
        url += f'?at={str(timestamp)}'
        headers = {'X-Signature': self.signature}
        result = requests.get(url=url, headers=headers)
        return result.json()

    def get_ticker(self):
        path = [self.base_url, 'indices', 'global', 'ticker', 'BTCUSD']
        url = '/'.join(path)
        headers = {'X-Signature': self.signature}
        result = requests.get(url=url, headers=headers)
        return result.json()


if __name__ == '__main__':
    price = BitcoinAverage().get_ticker()
    timestamp = price['timestamp']
    price_datetime = datetime.fromtimestamp(timestamp)

    year_directory = os.path.join(CACHE_PATH, str(price_datetime.year))
    if not os.path.exists(year_directory):
        os.mkdir(year_directory)
    month_directory = os.path.join(year_directory, str(price_datetime.month))
    if not os.path.exists(month_directory):
        os.mkdir(month_directory)
    day_directory = os.path.join(month_directory, str(price_datetime.day))
    if not os.path.exists(day_directory):
        os.mkdir(day_directory)

    file_path = os.path.join(day_directory, f'{timestamp}.json')

    with open(file_path, 'w') as f:
        json.dump(price, f)

