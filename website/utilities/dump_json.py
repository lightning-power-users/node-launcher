import json
import os
from decimal import Decimal

from bitcoin.core import COIN

from website.utilities.cache.get_cache_directory_by_date import (
    get_cache_directory_by_date
)


class FeeEstimateJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return int(o * COIN / 1000)
        return super(FeeEstimateJSONEncoder, self).default(o)


def dump_json(data, name, date):
    day_directory = get_cache_directory_by_date(date)
    file_path = os.path.join(day_directory, f'{date.hour}-{name}.json')
    with open(file_path, 'w') as f:
        if name == 'fee_estimate':
            json.dump(
                data,
                f,
                cls=FeeEstimateJSONEncoder,
                indent=4,
                sort_keys=True
            )
        else:
            if name == 'usd_price':
                json.dump(
                    data,
                    f,
                    indent=4,
                    sort_keys=True
                )
