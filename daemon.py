#!/usr/bin/env python

import asyncio
import websockets
import math
import time

SUBS = {}
RAW_DATA_TOPIC = "/raw"
MAIN_DATA_TOPIC = "/data"

def produce_raw():
    return 1000

def produce_data():
    return math.sin(time.time())

async def subscribe(websocket, path):
    print("Connected to {0}:{1}".format(websocket.remote_address, path))
    if path not in SUBS:
        SUBS[path] = set()
    
    SUBS[path].add(websocket)
    await publish(websocket, path)
        
async def unsubscribe(websocket, path):
    SUBS[path].remove(websocket)

async def publish(websocket, topic):
    try: 
        while 1:
            val = 0
            if topic == MAIN_DATA_TOPIC:
                val = produce_data()
            elif topic == RAW_DATA_TOPIC:
                val = produce_raw()
            else:
                print("[WARN] Topic undefined")
                await asyncio.sleep(0.5)    
                continue

            await websocket.send(str(val))
            await asyncio.sleep(0.5)    
    except websockets.exceptions.ConnectionClosedError:
        print("Connection Lost")
    finally:
        await unsubscribe(websocket, topic)


start_server = websockets.serve(subscribe, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_until_complete(publish(MAIN_DATA_TOPIC))
asyncio.get_event_loop().run_forever()