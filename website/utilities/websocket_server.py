import asyncio
import json
import time

import websockets
from google.protobuf.json_format import MessageToDict

from node_launcher.logging import log
from tools.lnd_client import lnd_remote_client
from website.constants import FLASK_SECRET_KEY


async def serve_invoices(websocket, path):
    invoices = {}
    # while True:
    tracker_data = await websocket.recv()
    if tracker_data:
        try:
            tracker_data = json.loads(tracker_data)
        except:
            log.error('error loading json', exc_info=True)
            return

    tracker = tracker_data.get('tracker', None)
    if not tracker:
        return

    if tracker == FLASK_SECRET_KEY:
        data = tracker_data
        invoice_data = data['invoice']
        invoices[invoice_data['r_hash']] = data
        log.debug('received from server', data=data)
        return

    invoice_subscription = lnd_remote_client.subscribe_invoices(settle_index=1)
    for invoice in invoice_subscription:
        invoice_data = MessageToDict(invoice)
        if invoice_data['r_hash'] not in invoices:
            time.sleep(2)
            await websocket.send(json.dumps(invoice_data))
            break
            # TODO: check on disk
            log.warn('r_hash not found in memory', invoice_data=invoice_data)
            continue
        data = invoice_data['r_hash']
        if data['tracker'] != tracker:
            continue
        log.debug('emit invoice', invoice=invoice)
        await websocket.send(json.dumps(invoice_data))
        break





start_server = websockets.serve(serve_invoices, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
