import os
import string
import random
from decimal import Decimal
from os.path import expanduser
from typing import Dict

from node_launcher.constants import (
    DARWIN,
    LINUX,
    OPERATING_SYSTEM,
    OperatingSystem,
    WINDOWS,
    LOCALAPPDATA)


default_secret_key = ''.join(
    random.choice(string.ascii_uppercase + string.digits) for _ in
    range(20))
FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', default_secret_key)

WEBSITE_DATA_PATHS: Dict[OperatingSystem, str] = {
    DARWIN: expanduser('~/Library/Application Support/Node Website/'),
    LINUX: expanduser('~/.node_website'),
    WINDOWS: os.path.join(LOCALAPPDATA, 'Node Website')
}
WEBSITE_DATA_PATH = WEBSITE_DATA_PATHS[OPERATING_SYSTEM]

if not os.path.exists(WEBSITE_DATA_PATH):
    os.mkdir(WEBSITE_DATA_PATH)

CACHE_PATH = os.path.join(WEBSITE_DATA_PATH, 'cache')

if not os.path.exists(CACHE_PATH):
    os.mkdir(CACHE_PATH)

EXPECTED_BYTES = 500

CAPACITY_CHOICES = [500000, 1000000, 2000000, 5000000, 16777215]

CAPACITY_FEE_RATES = [
    (Decimal('0'), 'One week free'),
    (Decimal('0.02'), 'One month 2%'),
    (Decimal('0.1'), 'Six months 10%'),
    (Decimal('0.18'), 'One year 18%')
]