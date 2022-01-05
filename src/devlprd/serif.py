import logging
from typing import Optional
import serial
import serial.threaded as sthread
import serial.tools.list_ports as list_ports

from pydevlpr_protocol import unpack_serial, DataFormatException
from .config import Board

def find_port(vid: int) -> str:
    """Smart port searching for finding an Arduino.
    
    Parses metadata to figure out where your Arduino is to avoid
    hardcoding the address. If multiple are found, always takes the first in the list
    """

    port_list = list_ports.comports()
    for port in port_list:
        if vid == port.vid:
            return port.device   
    return ""


def connect_to_board(board: Board) -> serial.Serial:
    """Creates a serial connection to an Arduino if possible."""

    port = find_port(board['VID'])
    if port == "":
        logging.warning("No Board Found")
        return None
    try:
        serif = serial.serial_for_url(port, baudrate=board['BAUD'])
    except serial.SerialException as e:
        logging.error("Failed to open serial port {}: {}".format(port, e))
        return None
    return serif


class DevlprReader(sthread.Packetizer):
    """Extends Packetizer from pyserial threading module, async serial support."""
    
    TERMINATOR = bytes([1])  ## Assumed to be at the end of every message

    def __init__(self, daemon_state):
        super().__init__()
        self.daemon_state = daemon_state

    # NOTE: There is probably a better way to do this
    # this is a callable so it can serve as a Packetizer singleton factory
    # for the ReaderThread
    def __call__(self):
        return self

    def connection_made(self, transport: sthread.Protocol) -> None:
        super(DevlprReader, self).connection_made(transport)
        logging.info("Serial Port Opened")
        
    # Called on each new packet (packet + TERMINATOR) from the serial port
    def handle_packet(self, packet: bytes) -> None:
        # Always buffer, custom callbacks are further up the stack
        try:
            (pin, data) = unpack_serial(packet)  # Split into payload and topic
            # logging.debug(print(f'PIN:{pin},DATA:{data}'))
        except DataFormatException:   # If the packet is invalid
            return
        
        self.daemon_state.enqueue_serial_data(pin, data)

    def connection_lost(self, exc: Exception) -> None:
        if exc:
            logging.error("Connection Lost : {}".format(exc))
        logging.info("Serial Port Closed")


class DevlprSerif:
    """Devlpr Ser(ial) i(nter)f(ace). Manages the threaded serial data connection with a DEVLPR board."""

    def __init__(self, board: Board) -> None:
        self.board = board
        self.reader_thread: Optional[sthread.ReaderThread] = None
        self.devlpr_reader: Optional[DevlprReader] = None

    def init_serial(self, state) -> bool:
        """ First opens the port, then spins off a watcher thread
        so it doesn't block the main path of execution."""

        serif = connect_to_board(self.board)
        if serif is None:
            return False
        self.devlpr_reader = DevlprReader(state)
        self.reader_thread = sthread.ReaderThread(serif, self.devlpr_reader)
        self.reader_thread.start()
        return True

    def deinit_serial(self) -> None:
        """Disconnect from serial and close out threads."""

        if self.reader_thread is not None:
            try:
                self.reader_thread.close()
                self.reader_thread = None
            except:
                pass # Already closed!