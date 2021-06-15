#!/usr/bin/env python

import asyncio
import websockets
from websockets import server
from enum import Enum
from typing import Tuple
import math
import time
import random
import seriald

class PacketType(Enum):
    SUBSCRIBE = "s"
    DATA = "d"
    UNSUBSCRIBE = "u"

PROTOCOL = "|"
SUBS = {}
RAW_DATA_TOPIC = "raw"
MAIN_DATA_TOPIC = "data"
GRIP_RIGHT_TOPIC = "grip_right"
GRIP_LEFT_TOPIC = "grip_left"

# Package a message for sending using the agreed on protocol
def wrap(msg_type: PacketType, msg: str) -> str:
    return "{}{}{}".format(msg_type, PROTOCOL, msg)

# Unpackage a message into its command (type) and data
def unwrap(msg: str) -> Tuple[PacketType, str]:
    unwrapped = msg.split(PROTOCOL, maxsplit=1)
    if len(unwrapped) < 2:
        print("[Warn] Invalid message")
        return ("", "")
    return (unwrapped[0], unwrapped[1])

async def subscribe(websocket: server.WebSocketServerProtocol, path: str):
    print("Connected to {0}:{1} - {2}".format(websocket.remote_address[0], websocket.remote_address[1], path))
    if path not in SUBS:
        SUBS[path] = set()

    SUBS[path].add(websocket)
    print(SUBS)
    await publish(websocket, path)
        
async def unsubscribe(websocket: server.WebSocketServerProtocol, path: str):
    SUBS[path].remove(websocket)
    
async def receive(websocket: server.WebSocketServerProtocol):
    async for message in websocket:
        command, data = unwrap(message)
        if command == PacketType.SUBSCRIBE.value:
            # Call chain is weird here. The most recent channel is essentially responsible for
            # adding the next channel. This means no-one else can receive anything, but it
            # implicitly prevents duplicated subs and messages.
            await subscribe(websocket, data)

async def send(websocket, data, topic):
    while 1:
        while len(data) > 0:
            await websocket.send(wrap(topic, data.pop()))
        await asyncio.sleep(0.001) # Spin fast but also allow other tasks to hop in

async def publish(websocket: server.WebSocketServerProtocol, topic: str):
    DATA = list()
    produce = lambda data : DATA.append(data)
    recv_task = asyncio.create_task(receive(websocket))
    send_task = asyncio.create_task(send(websocket, DATA, topic))
    try: 
        if topic == RAW_DATA_TOPIC or topic == MAIN_DATA_TOPIC:
            seriald.add_callback(produce)
        # These run in parallel
        await recv_task
        await send_task

    except websockets.exceptions.ConnectionClosedError:
        print("Connection Lost Unexpectedly")
    except websockets.exceptions.ConnectionClosedOK:
        print("Disconnected from {0}:{1} - {2}".format(websocket.remote_address[0], websocket.remote_address[1], topic))
    finally:
        await unsubscribe(websocket, topic)
        if topic == RAW_DATA_TOPIC and len(SUBS[topic]) == 0:
            seriald.deinit_serial()


start_server = websockets.serve(subscribe, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()