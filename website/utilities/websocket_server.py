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

USERS = {}


async def register(tracker, websocket):
    USERS[tracker] = websocket


async def unregister(tracker):
    del USERS[tracker]


async def serve_invoices(websocket, path):
    data_string_from_client = await websocket.recv()

    # noinspection PyBroadException
    try:
        data_from_client = json.loads(data_string_from_client)
    except:
        log.error(
            'Error loading json',
            exc_info=True,
            data_string_from_client=data_string_from_client
        )
        return

    tracker = data_from_client.get('tracker', None)
    if not tracker:
        return

    if tracker == FLASK_SECRET_KEY:
        data_from_server = data_from_client
        invoice_data = data_from_server['invoice']
        # Todo: populate invoices from disk as well
        channel_opening_invoices[invoice_data['r_hash']] = data_from_server
        log.debug('Received from server', data_from_server=data_from_server)
        return

    await register(tracker, websocket)
    try:
        channel_opening_data = None
        # Todo find the minimum index of the cached invoices for settle_index
        invoice_subscription = lnd_remote_client.subscribe_invoices(settle_index=1)
        for invoice in invoice_subscription:
            invoice_data = MessageToDict(invoice)
            # Todo: always resolves to true for testing, remove
            if not True and invoice_data['r_hash'] not in channel_opening_invoices:
                # TODO: remove
                time.sleep(2)

                log.debug(
                    'r_hash not found in channel_opening_invoices',
                    invoice_data=invoice_data
                )
                continue

            channel_opening_data = channel_opening_invoices[invoice_data['r_hash']]
            if channel_opening_data.get('tracker', None) != tracker:
                continue

            log.debug('emit invoice', invoice=invoice)
            await websocket.send(json.dumps(invoice_data))
            break

        if channel_opening_data is not None:
            if channel_opening_data.get('reciprocation_capacity', None):
                local_funding_amount = channel_opening_data[
                    'reciprocation_capacity']
            else:
                local_funding_amount = int(
                    channel_opening_data['form_data']['capacity'])

            sat_per_byte = int(
                channel_opening_data['form_data']['transaction_fee_rate'])

            response = lnd_remote_client.open_channel(
                node_pubkey_string=channel_opening_data['parsed_pubkey'],
                local_funding_amount=local_funding_amount,
                push_sat=0,
                sat_per_byte=sat_per_byte,
                spend_unconfirmed=True
            )

            try:
                for update in response:
                    update_data = MessageToDict(update)
                    msg = {'open_channel_update': update_data}
                    await websocket.send(json.dumps(msg))
                    if update_data.get('chan_open', None):
                        break
            except _Rendezvous as e:
                error_details = e.details()
                error_message = {'error': error_details}
                await websocket.send(json.dumps(error_message))
    finally:
        await unregister(tracker)

start_server = websockets.serve(serve_invoices, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
