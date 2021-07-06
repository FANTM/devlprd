#!/usr/bin/env python

import asyncio
import logging
import websockets
from websockets import server

import serif
from protocol import *
from DaemonState import DaemonState

ADDRESS = ("localhost", 8765)  # (Address/IP, Port)
STATE: DaemonState = DaemonState()  # Make sure to pass this to any other threads that need access to shared state

logging.basicConfig(level=logging.INFO)

async def receive(websocket: server.WebSocketServerProtocol) -> None:
    async for message in websocket:
        command, data = unwrap_packet(message)
        if command == PacketType.SUBSCRIBE:
            logging.info("Sub to {}".format(data))
            STATE.subscribe(websocket, data)

async def daemon(websocket: server.WebSocketServerProtocol, path: str) -> None:
    logging.info("Connected to {0}:{1}".format(websocket.remote_address[0], websocket.remote_address[1]))
    try:
        await receive(websocket)
    finally:
        logging.info("Disconnected from {0}:{1}".format(websocket.remote_address[0], websocket.remote_address[1]))
        STATE.unsubscribe_all(websocket)

def main() -> None:
    loop = asyncio.get_event_loop()
    serif.init_serial(STATE, loop)
    start_server = websockets.server.serve(daemon, ADDRESS[0], ADDRESS[1])
    loop.run_until_complete(start_server)
    loop.run_forever()

if __name__ == "__main__":
    main()