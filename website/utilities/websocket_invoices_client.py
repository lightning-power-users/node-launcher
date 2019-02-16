import asyncio
import json
import threading

import websockets
from google.protobuf.json_format import MessageToDict

from node_launcher.logging import log
from tools.lnd_client import lnd_remote_client
from website.constants import FLASK_SECRET_KEY


def emit_invoices():
    async def send_to_server():
        async with websockets.connect('ws://localhost:8765') as websocket:
            invoice_subscription = lnd_remote_client.subscribe_invoices(settle_index=1)
            for invoice in invoice_subscription:
                data = {
                    'tracker': FLASK_SECRET_KEY,
                    'invoice_data': MessageToDict(invoice)
                }
                data_string = json.dumps(data)
                log.debug('sending websocket message', data=data)
                await websocket.send(data_string)

    def worker(loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_to_server())

    loop = asyncio.new_event_loop()
    p = threading.Thread(target=worker, args=[loop])
    p.start()


if __name__ == '__main__':
    emit_invoices()
