from collections import deque
import logging

from protocol import *
from typing import Dict, Deque
import serial
import serial.threaded as sthread
import serial.tools.list_ports as list_ports

BAUD = 2000000
SERIAL_DATA: Dict[int, Deque[int]] = dict()
BUFFER_SIZE = 155
serial_worker: sthread.ReaderThread = None
devlpr_reader: sthread.Packetizer = None

class DevlprReader(sthread.Packetizer):
    TERMINATOR = b'\r\n'
    def __call__(self):
        return self

    def connection_made(self, transport: sthread.Protocol) -> None:
        super(DevlprReader, self).connection_made(transport)
        logging.info('Serial Port Opened')
        
    # Called on each new line (data + TERMINATOR) from the serial port
    def handle_packet(self, raw: bytes) -> None:
        # Always buffer, custom callbacks are further up the stack
        try:
            (pin, data) = unpack_serial(raw)  # Split into payload and topic
        except DataFormatException:   # If the packet is invalid
            return
        if pin not in SERIAL_DATA:
            SERIAL_DATA[pin] = deque(maxlen=BUFFER_SIZE)
        SERIAL_DATA[pin].appendleft(data)

    def connection_lost(self, exc: Exception) -> None:
        if exc:
            logging.error("Connection Lost : {}".format(exc))
        logging.info("Serial Port Closed")

# Smart port searching, parses metadata to figure out where your Arduino is to avoid
# hardcoding the address. If multiple are found, always takes the first in the list
def find_port() -> str:
    port_list = list_ports.comports()
    for port in port_list:
        if 'arduino' in port.description.lower():
            return port.device   
    return ""

# Open the serial port to an ardunio
def connect_to_arduino() -> serial.Serial:
    port = find_port()
    if port == "":
        logging.error("No Arduino Found")
        return None
    try:
        serif = serial.serial_for_url(port, baudrate=BAUD)
    except serial.SerialException as e:
        logging.error('Failed to open serial port {}: {}'.format(port, e))
        return None
    return serif

# First opens the port, then spins off a watcher into another thread so
# it doesn't block the main path of execution.
def init_serial() -> None:
    global serial_worker, devlpr_reader
    serif = connect_to_arduino()
    if serif is None:
        return
    devlpr_reader = DevlprReader()
    serial_worker = sthread.ReaderThread(serif, DevlprReader)
    serial_worker.start()

# Shut it down!
def deinit_serial() -> None:
    global serial_worker, devlpr_reader
    if serial_worker is not None:
        serial_worker.stop()
    serial_worker = None
    devlpr_reader = None
