#!/usr/bin/env python

import asyncio
import logging
import websockets as ws
import serif
import protocol
import DaemonState as ds

ADDRESS = ("localhost", 8765)  # (Address/IP, Port)
state: ds.DaemonState = ds.DaemonState()  # Make sure to pass this to any other threads that need access to shared state
devlpr_serial: serif.DevlprSerif = serif.DevlprSerif()

logging.basicConfig(level=logging.INFO)

async def receive(websocket: ws.server.WebSocketServerProtocol) -> None:
    """Delegate and process incoming messages from a websocket connection."""

    async for message in websocket:
        command, data = protocol.unwrap_packet(message)
        if command == protocol.PacketType.SUBSCRIBE:
            logging.info("Sub to {}".format(data))
            state.subscribe(websocket, data)

async def daemon(websocket: ws.server.WebSocketServerProtocol, path: str) -> None:
    """Main function for websocket connections. Holds the connection until the other side disconnects."""

    logging.info("Connected to {0}:{1}".format(websocket.remote_address[0], websocket.remote_address[1]))
    try:
        await receive(websocket)
    finally:
        logging.info("Disconnected from {0}:{1}".format(websocket.remote_address[0], websocket.remote_address[1]))
        state.unsubscribe_all(websocket)

async def startup() -> None:
    """Initiallizes both the serial connection and the websocket server. It then just hangs until everything is done internally before cleaning up."""

    global state
    state.event_loop = asyncio.get_event_loop()
    devlpr_serial.init_serial(state)
    state.start_server = ws.server.serve(daemon, ADDRESS[0], ADDRESS[1])
    async with state.start_server as server:
        state.server = server
        await server.wait_closed()
    devlpr_serial.deinit_serial()

def shutdown() -> None:
    """Manually closes out the server. Most of the time you don't need to do this because it should close when you exit the program."""
    
    global state
    try: 
        state.server.close()
        asyncio.run_coroutine_threadsafe(state.server.wait_closed(), loop=state.event_loop)
    except AttributeError:
        pass  # Already closed and gone
    devlpr_serial.deinit_serial()

def main() -> None:
    asyncio.run(startup())

if __name__ == "__main__":
    main()
