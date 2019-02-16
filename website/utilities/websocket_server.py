import asyncio
import json
import time

import websockets
from google.protobuf.json_format import MessageToDict
from grpc._channel import _Rendezvous

from node_launcher.logging import log
from tools.lnd_client import lnd_remote_client
from website.constants import FLASK_SECRET_KEY


channel_opening_invoices = {}


async def serve_invoices(websocket, path):
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
        # Todo: populate invoices from disk as well
        channel_opening_invoices[invoice_data['r_hash']] = data
        log.debug('received from server', data=data)
        return

    channel_opening_data = None
    invoice_subscription = lnd_remote_client.subscribe_invoices(settle_index=1)
    for invoice in invoice_subscription:
        invoice_data = MessageToDict(invoice)
        # Todo: always resolves to true for testing, remove
        if not True and invoice_data['r_hash'] not in channel_opening_invoices:
            # TODO: remove
            time.sleep(2)

            # TODO: check on disk
            log.warn('r_hash not found in memory', invoice_data=invoice_data)
            continue
        channel_opening_data = channel_opening_invoices[invoice_data['r_hash']]
        if channel_opening_data.get('tracker', None) != tracker:
            continue
        log.debug('emit invoice', invoice=invoice)
        await websocket.send(json.dumps(invoice_data))
        break

    if channel_opening_data is not None:
        if channel_opening_data.get('reciprocation_capacity', None):
            local_funding_amount = channel_opening_data['reciprocation_capacity']
        else:
            local_funding_amount = int(channel_opening_data['form_data']['capacity'])

        sat_per_byte = int(channel_opening_data['form_data']['transaction_fee_rate'])

        response = lnd_remote_client.open_channel(
            node_pubkey_string=channel_opening_data['parsed_pubkey'],
            local_funding_amount=local_funding_amount,
            push_sat=0,
            sat_per_byte=sat_per_byte,
            spend_unconfirmed=True
        )

        try:
            for update in response:
                update_data = {'open_channel_update': MessageToDict(update)}
                await websocket.send(json.dumps(update_data))
        except _Rendezvous as e:
            error_details = e.details()
            error_message = {'error': error_details}
            await websocket.send(json.dumps(error_message))

start_server = websockets.serve(serve_invoices, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
