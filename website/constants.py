import os
import string
import random

from node_launcher.constants import OPERATING_SYSTEM, NODE_LAUNCHER_DATA_PATH

default_secret_key = ''.join(
    random.choice(string.ascii_uppercase + string.digits) for _ in
    range(20))
FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', default_secret_key)

network = 'mainnet'


cache_path = os.path.join(NODE_LAUNCHER_DATA_PATH[OPERATING_SYSTEM],
                          'webapp_cache')

if not os.path.exists(cache_path):
    os.mkdir(cache_path)
