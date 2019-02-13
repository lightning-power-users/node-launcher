import hashlib
import hmac
import json
import os
import time
from datetime import datetime

import requests

from website.utilities.cache_directory import get_directory, dump_json


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


def output_price():
    price = BitcoinAverage().get_ticker()
    timestamp = price['timestamp']
    price_datetime = datetime.fromtimestamp(timestamp)
    dump_json(data=price, name='usd_price', date=price_datetime)


if __name__ == '__main__':
    output_price()
