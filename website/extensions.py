from flask_caching import Cache
from flask_socketio import SocketIO

cache = Cache(config={'CACHE_TYPE': 'simple'})

socketio = SocketIO(async_mode='gevent', message_queue='redis://')
