import asyncio
import json
import threading

import websockets

from node_launcher.logging import log
from website.constants import FLASK_SECRET_KEY


def emit_invoices():
    async def send_to_server():
        async with websockets.connect('ws://localhost:8765') as websocket:
            data['tracker'] = FLASK_SECRET_KEY

            data_string = json.dumps(data)
            await websocket.send(data_string)
            log.debug('sending websocket message', data=data)

    def worker(loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_to_server())

    loop = asyncio.new_event_loop()
    p = threading.Thread(target=worker, args=[loop])
    p.start()


if __name__ == '__main__':
    emit_invoices()
