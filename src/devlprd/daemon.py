import asyncio
import logging
import websockets as ws
from .serif import DevlprSerif
from .DaemonState import DaemonState

ADDRESS = ("localhost", 8765)  # (Address/IP, Port)
ws_server: ws.server.WebSocketServer = None
state: DaemonState = DaemonState()  # Make sure to pass this to any other threads that need access to shared state
devlpr_serial: DevlprSerif = DevlprSerif()

logging.basicConfig(level=logging.INFO)

async def ws_accept(websocket: ws.server.WebSocketServerProtocol) -> None:
    """Delegate and process incoming messages from a websocket connection."""
    
    from .protocol import unwrap_packet, PacketType
    async for message in websocket:
        command, data = unwrap_packet(message)
        if command == PacketType.SUBSCRIBE:
            logging.info("Sub to {}".format(data))
            state.subscribe(websocket, data)

async def ws_handler(websocket: ws.server.WebSocketServerProtocol, path: str) -> None:
    """Main function for websocket connections. Holds the connection until the other side disconnects."""

    logging.info("Connected to {0}:{1}".format(websocket.remote_address[0], websocket.remote_address[1]))
    try:
        await ws_accept(websocket)
    finally:
        logging.info("Disconnected from {0}:{1}".format(websocket.remote_address[0], websocket.remote_address[1]))
        state.unsubscribe_all(websocket)

async def startup() -> None:
    """Initiallizes both the serial connection and the websocket server. It then just hangs until everything is done internally before cleaning up."""

    devlpr_serial.init_serial(state)
    ws_server = ws.server.serve(ws_handler, ADDRESS[0], ADDRESS[1])
    async with ws_server as server:
        await server.wait_closed()
    devlpr_serial.deinit_serial()

def shutdown() -> None:
    """Manually closes out the server. Most of the time you don't need to do this because it should close when you exit the program."""

    try:
        ws_server.close()
    except AttributeError:
        pass  # Already closed and gone
    devlpr_serial.deinit_serial()