#!/usr/bin/env python

import asyncio
import logging
from typing import Dict, List

import websockets
from websockets import server

import serif
from protocol import *

ADDRESS = ("localhost", 8765)  # (Address/IP, Port)
SUBS: Dict[str, List[server.WebSocketServerProtocol]] = dict()

logging.basicConfig(level=logging.INFO)

def subscribe(websocket: server.WebSocketServerProtocol, topic: str):
    try:
        SUBS[topic].append(websocket)
    except KeyError:
        SUBS[topic] = list()
        SUBS[topic].append(websocket)

def unsubscribe(websocket: server.WebSocketServerProtocol, path: str):
    try:
        SUBS[path].remove(websocket)
    except:
        logging.warning("Trying to unsubscribe w/o ever subscribing")
        
async def receive(websocket: server.WebSocketServerProtocol):
    async for message in websocket:
        command, data = unwrap_packet(message)
        if command == PacketType.SUBSCRIBE:
            logging.info("Sub to {}".format(data))
            subscribe(websocket, data)

async def daemon(websocket: server.WebSocketServerProtocol, path: str):
    logging.info("Connected to {0}:{1} - {2}".format(websocket.remote_address[0], websocket.remote_address[1], path))
    try:
        await receive(websocket)
    except websockets.exceptions.ConnectionClosed:
        logging.info("Disconnected from {0}:{1}".format(websocket.remote_address[0], websocket.remote_address[1], path))
        unsubscribe(websocket)


async def pub(topic: str, pin: int, data: str):
    try:
        await asyncio.wait([sub.send(wrap_packet(topic, pin, data)) for sub in SUBS[topic]])
    except:
        pass

def main():
    serif.init_serial()
    start_server = websockets.serve(daemon, ADDRESS[0], ADDRESS[1])
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()