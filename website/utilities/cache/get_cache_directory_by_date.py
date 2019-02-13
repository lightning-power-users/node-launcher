import os
from datetime import datetime

from website.constants import CACHE_PATH


def get_cache_directory_by_date(date_time: datetime):
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
