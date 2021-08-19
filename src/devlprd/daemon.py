import asyncio
import logging
import websockets as ws
from .serif import DevlprSerif
from .DaemonState import DaemonState

ADDRESS = ("localhost", 8765)  # (Address/IP, Port)
ws_server: ws.server.WebSocketServer = None
state: DaemonState = None  # Make sure to pass this to any other threads that need access to shared state
devlpr_serial: DevlprSerif = None

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

    global ws_server
    global state
    global devlpr_serial
    # we'll want the asyncio event loop for subscriptions, some processing, and publishing
    event_loop = asyncio.get_running_loop()
    # the DaemonState requests publishes upon state change, so needs to know the event loop
    state = DaemonState(event_loop)
    # we initialize our serial connection, which is managed on a separate thread
    devlpr_serial = DevlprSerif()
    devlpr_serial.init_serial(state)
    # and now we serve websockets, waiting for incoming subscribers to data (pydevlpr and other libraries)
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