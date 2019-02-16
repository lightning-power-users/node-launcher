import json
import os
from datetime import datetime
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


def dump_json(data, name, date=None, label=None):
    if date is None:
        date = datetime.now()
    if label is None:
        label = date.hour
    day_directory = get_cache_directory_by_date(date)
    file_path = os.path.join(day_directory, f'{name}-{label}.json')
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
            json.dump(
                data,
                f,
                indent=4,
                sort_keys=True
            )
