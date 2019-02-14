from wsgiref.simple_server import make_server

import socketio

from node_launcher.logging import log

if __name__ == '__main__':
    mgr = socketio.RedisManager('redis://')

    sio = socketio.Server(client_manager=mgr)


    @sio.on('connect')
    def connect(sid, environ):
        log.debug('connect ', sid)

    @sio.on('disconnect')
    def disconnect(sid):
        log.debug('disconnect ', sid)

    @sio.on('invoice')
    def handle_invoice(sid, data):
        log.debug('invoice seen on server', data)

    app = socketio.WSGIApp(sio)
    with make_server('localhost', 8888, app) as httpd:
        httpd.serve_forever()
