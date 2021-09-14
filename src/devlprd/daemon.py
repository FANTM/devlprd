import asyncio
import multiprocessing as mp
import logging
from pydevlpr_protocol import DataFormatException, unwrap_packet, PacketType, DaemonSocket

from .serif import DevlprSerif
from .DaemonState import DaemonState
from .config import CONFIG

server = None
state: DaemonState = None  # Make sure to pass this to any other threads that need access to shared state
devlpr_serial: DevlprSerif = None

logging.basicConfig(level=logging.INFO)

class DaemonController:

    def start(self, block=False):
        self.p = mp.Process(target=main)
        self.p.start()
        if block:
            self.p.join()

    def stop(self):
        if self.p is not None and self.p.is_alive():
            self.p.terminate()

def main():
    asyncio.run(startup())

async def client_accept(sock: DaemonSocket) -> None:
    """Delegate and process incoming messages from a websocket connection."""

    message = ' '
    while len(message) > 0:
        message = await sock.recv()
        if len(message) > 0:
            try:
                command, data = unwrap_packet(message)
            except DataFormatException:
                continue  # Handle an unexpected issue with the packet
            if command == PacketType.SUBSCRIBE:
                logging.info("Sub to {}".format(data))
                state.subscribe(sock, data)

async def client_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Main function for socket connections. Holds the connection until the other side disconnects."""

    dsock = DaemonSocket(reader, writer)
    logging.info("Connected to {0}".format(dsock.get_remote_address()))
    try:
        await client_accept(dsock)
    finally:
        logging.info("Disconnected from {0}".format(dsock.get_remote_address()))
        state.unsubscribe_all(dsock)


async def startup() -> None:
    """Initiallizes both the serial connection and the socket server. It then just hangs until everything is done internally before cleaning up."""

    global server
    global state
    global devlpr_serial
    # we'll want the asyncio event loop for subscriptions, some processing, and publishing
    event_loop = asyncio.get_running_loop()
    # the DaemonState requests publishes upon state change, so needs to know the event loop
    state = DaemonState(event_loop)
    # we initialize our serial connection, which is managed on a separate thread
    devlpr_serial = DevlprSerif()
    devlpr_serial.init_serial(state)
    # start a server, waiting for incoming subscribers to data (pydevlpr and other libraries)
    server = await asyncio.start_server(client_handler, CONFIG['ADDRESS'][0], CONFIG['ADDRESS'][1])
    async with server:
        await server.serve_forever()
    print("Finish up")
    devlpr_serial.deinit_serial()

def shutdown() -> None:
    """Manually closes out the server. Most of the time you don't need to do this because it should close when you exit the program."""
    global server_task
    global server
    try:
        server.close()
        asyncio.run_coroutine_threadsafe(server.wait_closed(), asyncio.get_event_loop())
    except AttributeError:
        pass  # Already closed and gone
    print("Wrap up?")