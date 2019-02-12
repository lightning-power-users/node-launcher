import os
import string
import random
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
