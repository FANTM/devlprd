#!/usr/bin/env python

import asyncio
import websockets
from websockets import server
import math
import time
import random
import seriald

SUBS = {}
RAW_DATA_TOPIC = "/raw"
MAIN_DATA_TOPIC = "/data"
BOOL_DATA_TOPIC = "/grip_right"


def produce_raw(data):
    DATA.append(data)    

def produce_data():
    return math.sin(time.time())

def produce_bool():
    return random.choice([True, False])

async def subscribe(websocket: server.WebSocketServerProtocol, path: str):
    print("Connected to {0}:{1} - {2}".format(websocket.remote_address[0], websocket.remote_address[1], path))
    if path not in SUBS:
        SUBS[path] = set()
    
    # if path == RAW_DATA_TOPIC and len(SUBS[path]) == 0:
    #     seriald.init_serial()

    SUBS[path].add(websocket)
    await publish(websocket, path)
        
async def unsubscribe(websocket: server.WebSocketServerProtocol, path: str):
    SUBS[path].remove(websocket)
    

async def publish(websocket: server.WebSocketServerProtocol, topic: str):
    DATA = list()
    produce = lambda data : DATA.append(data)
    try: 
        if topic == RAW_DATA_TOPIC:
            seriald.add_callback(produce)
        while 1:
            while len(DATA) > 0:
                await websocket.send(DATA.pop())
            await asyncio.sleep(0.001)
    except websockets.exceptions.ConnectionClosedError:
        print("Connection Lost Unexpectedly")
    except websockets.exceptions.ConnectionClosedOK:
        print("Disconnected from {0}:{1} - {2}".format(websocket.remote_address[0], websocket.remote_address[1], topic))
    finally:
        await unsubscribe(websocket, topic)
        if topic == RAW_DATA_TOPIC and len(SUBS[topic]) == 0:
            print("DE_INIT")
            seriald.deinit_serial()


start_server = websockets.serve(subscribe, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()