#!/usr/bin/env python

import asyncio
import logging
from typing import List

import websockets
from websockets import server

import serif
from protocol import *

CONN_INFO = ("localhost", 8765)  # (Address/IP, Port)
SUBS = {}

logging.basicConfig(level=logging.INFO)

async def subscribe(websocket: server.WebSocketServerProtocol, path: str):
    logging.info("Connected to {0}:{1} - {2}".format(websocket.remote_address[0], websocket.remote_address[1], path))
    if path not in SUBS:  # Create set if this is the first sub to a topic
        SUBS[path] = set()

    SUBS[path].add(websocket)  # Add subscriber for managing later
    await publish(websocket, path)  # Loop that manages connection past subscription. Doesn't return while connected

def unsubscribe(websocket: server.WebSocketServerProtocol, path: str):
    SUBS[path].remove(websocket)
    
async def receive(websocket: server.WebSocketServerProtocol):
    async for message in websocket:
        command, data = unwrap_packet(message)
        if command == PacketType.SUBSCRIBE.value:
            # Call chain is weird here. The most recent channel is essentially responsible for
            # adding the next channel. This means no-one else can receive anything, but it
            # implicitly prevents duplicated subs and messages.
            await subscribe(websocket, data)

async def send(websocket: server.WebSocketServerProtocol, data: List[float], topic: str):
    while websocket.open:
        # If there is any new data in the buffer, we will empty it out over the pipe
        while len(data) > 0:
            await websocket.send(wrap_packet(topic, data.pop()))
        await asyncio.sleep(0.001)  # Spin fast but also allow other tasks to hop in

async def publish(websocket: server.WebSocketServerProtocol, topic: str):
    DATA = list()  # Buffer used by other layers to pile in data
    try: 
        serif.add_callback(topic, DATA.append)  # Add data to buffer as it's recv'd in serial  
        await asyncio.gather(receive(websocket), send(websocket, DATA, topic))  # Run send + recv in parallel, indefinitely
    except websockets.exceptions.ConnectionClosedError:
        logging.warning("Connection Lost Unexpectedly")
    except websockets.exceptions.ConnectionClosedOK:
        logging.info("Disconnected from {0}:{1} - {2}".format(websocket.remote_address[0], websocket.remote_address[1], topic))
    finally:
        # Disconnects socket + topics
        logging.info("Disconnected from {0}:{1} - {2}".format(websocket.remote_address[0], websocket.remote_address[1], topic))
        unsubscribe(websocket, topic)

start_server = websockets.serve(subscribe, CONN_INFO[0], CONN_INFO[1])
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
