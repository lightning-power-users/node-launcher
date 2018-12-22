import os
import string
import random

from node_launcher.node_set import NodeSet

default_secret_key = ''.join(
    random.choice(string.ascii_uppercase + string.digits) for _ in
    range(20))
FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', default_secret_key)


node_set = NodeSet('mainnet')
