import json
import os
from datetime import datetime
from decimal import Decimal

from bitcoin.core import COIN

from website.constants import CACHE_PATH


class FeeEstimateJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return int(o * COIN / 1000)
        return super(FeeEstimateJSONEncoder, self).default(o)


def get_directory(date_time: datetime):
    year_directory = os.path.join(CACHE_PATH, str(date_time.year))
    if not os.path.exists(year_directory):
        os.mkdir(year_directory)
    month_directory = os.path.join(year_directory, str(date_time.month))
    if not os.path.exists(month_directory):
        os.mkdir(month_directory)
    day_directory = os.path.join(month_directory, str(date_time.day))
    if not os.path.exists(day_directory):
        os.mkdir(day_directory)
    return day_directory


def dump_json(data, name, date):
    day_directory = get_directory(date)
    file_path = os.path.join(day_directory, f'{date.hour}-{name}.json')
    with open(file_path, 'w') as f:
        json.dump(
            data,
            f,
            cls=FeeEstimateJSONEncoder,
            indent=4,
            sort_keys=True
        )
