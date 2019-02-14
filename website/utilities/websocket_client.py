#!/usr/bin/env python

# WS client example

import asyncio
import websockets

from node_launcher.logging import log


async def hello():
    async with websockets.connect('ws://localhost:8765') as websocket:
        while True:
            message = await websocket.recv()
            log.info('received message', data=message)

asyncio.get_event_loop().run_until_complete(hello())
