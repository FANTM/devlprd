import asyncio
import multiprocessing as mp
import logging
from typing import Optional
from pydevlpr_protocol import DataFormatException, unwrap_packet, PacketType, DaemonSocket

from .serif import DevlprSerif
from .DaemonState import DaemonState
from .config import BOARDS, Board, ADDRESS

server = None
state: Optional[DaemonState] = None  # Make sure to pass this to any other threads that need access to shared state
devlpr_serial: Optional[DevlprSerif] = None

logging.basicConfig(level=logging.INFO, format=f'%(levelname)s:{__name__}:%(message)s')

class DaemonController:
    def __init__(self, board_id: str) -> None:
        self.board_id = board_id

    def start(self, block=False):
        self.p = mp.Process(target=main, args=(self.board_id,))
        self.p.start()
        if block:
            try:
                self.p.join()
            except KeyboardInterrupt:
                self.p.kill()

    def stop(self):
        if self.p is not None and self.p.is_alive():
            self.p.terminate()

def main(board_id: str):
    try:
        board = BOARDS[board_id]
    except KeyError:
        logging.warning("Invalid board ID, try get_board_ids() for options")
        logging.info('Assuming DEVLPR')
        board = BOARDS['DEVLPR']

    asyncio.run(startup(board))

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
                logging.info("Subscribing to {}".format(data))
                try:
                    state.subscribe(sock, data)
                except AttributeError:
                    logging.error("Failed to subscribe, Daemon State is None")

async def client_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Main function for socket connections. Holds the connection until the other side disconnects."""
    
    logging.debug("Incoming Connection")
    dsock = DaemonSocket(reader, writer)
    logging.info("Connected to {0}".format(dsock.get_remote_address()))
    try:
        await client_accept(dsock)
    except (BrokenPipeError, ConnectionError):
        pass  # Happens if we disconnect non-gracefully, but it's generally fine I think
    finally:
        logging.info("Disconnected from {0}".format(dsock.get_remote_address()))
        try:
            state.unsubscribe_all(dsock)
        except AttributeError:
            logging.error("Failed to unsubscribe_all, Daemon State is None")

async def startup(board: Board) -> None:
    """Initiallizes both the serial connection and the socket server. It then just hangs until everything is done internally before cleaning up."""

    global server
    global state
    global devlpr_serial
    # we'll want the asyncio event loop for subscriptions, some processing, and publishing
    event_loop = asyncio.get_running_loop()
    # the DaemonState requests publishes upon state change, so needs to know the event loop
    state = DaemonState(event_loop, board)
    # we initialize our serial connection, which is managed on a separate thread
    devlpr_serial = DevlprSerif(board)
    devlpr_serial.init_serial(state)
    # start a server, waiting for incoming subscribers to data (pydevlpr and other libraries)
    server = await asyncio.start_server(client_handler, ADDRESS[0], ADDRESS[1])
    try:
        logging.debug("Started Listening")
        await server.serve_forever()
    except (asyncio.exceptions.CancelledError):
        logging.debug("Closing Server")
        await server.wait_closed()
        
    devlpr_serial.deinit_serial()

def shutdown() -> None:
    """Manually closes out the server. Most of the time you don't need to do this because it should close when you exit the program."""
    
    global server
    global devlpr_serial
    try:
        if server is not None and server.is_serving():
            server.close()
            # asyncio.run_coroutine_threadsafe(server.wait_closed(), asyncio.get_event_loop())
    except:
        pass 
    try:
        devlpr_serial.deinit_serial()
    except AttributeError:
        logging.warning("Serial couldn't close because devlpr_serial is already None")
    except:
        pass # not even sure this is necessary

# TODO this should all probably be part of an object rather than global state
def _get_state():
    global state
    return state
