import socketio
from google.protobuf.json_format import MessageToDict

from node_launcher.logging import log
from tools.lnd_client import lnd_remote_client

external_sio = socketio.RedisManager('redis://', write_only=True)

subscription = lnd_remote_client.subscribe_invoices(settle_index=1)

for invoice in subscription:
    invoice_data = MessageToDict(invoice)
    log.debug('emit invoice', invoice=invoice)
    external_sio.emit('invoice', data=invoice_data, room='invoices')
