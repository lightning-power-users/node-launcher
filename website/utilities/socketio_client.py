import socketio
from google.protobuf.json_format import MessageToDict

from node_launcher.logging import log
from tools.lnd_client import lnd_remote_client

sio = socketio.Client()


@sio.on('connect')
def on_connect():
    print('Im connected!')

    subscription = lnd_remote_client.subscribe_invoices(settle_index=1)

    for invoice in subscription:
        invoice_data = MessageToDict(invoice)
        log.debug('emit invoice', invoice=invoice)
        sio.emit('invoice', data=invoice_data)



@sio.on('invoice')
def invoice_was_paid(sid, invoice):
    log.debug('invoice_was_paid', sid=sid, invoice=invoice)
    print('invoice')


@sio.on('disconnect')
def on_disconnect():
    print('Im disconnected!')


sio.connect('ws://localhost:8888', transports='websocket')
