import logging
import asyncio
import serial
import websockets

logging.basicConfig(level=logging.INFO)

SUBSCRIBERS = set()

async def subscribe(websocket, path):
    SUBSCRIBERS.add(websocket)
    logging.info('subscribed to messages: {0}'.format(websocket))

async def notify_subscribers(msg):
    logging.info('notifying subscribers')
    if SUBSCRIBERS:
        await asyncio.wait([sub.send(msg) for sub in SUBSCRIBERS])

async def update_emg_data(websocket, path):
    try:
        async for message in websocket:
            notify_subscribers(message)
    finally:
        logging.info('hit finally in update_emg_data')

update_server = websockets.serve(update_emg_data, 'localhost', 6789)
subscribe_server = websockets.serve(subscribe, 'localhost', 6790)

logging.info('here we go')
asyncio.get_event_loop().run_until_complete(update_server)
logging.info('and again')
asyncio.get_event_loop().run_until_complete(subscribe_server)
logging.info('and run forever')
asyncio.get_event_loop().run_forever()