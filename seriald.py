import logging
from protocol import *
from typing import Dict, List
import serial
from collections.abc import Callable
import serial.threaded as sthread
import serial.tools.list_ports as list_ports
import sys

BAUD = 115200
serial_worker: serial.Serial = None
devlpr_reader: sthread.LineReader = None

class DevlprReader(sthread.LineReader):
    read_callbacks: Dict[str, List[Callable[[str], None]]] = dict()
    def __call__(self):
        return self

    def connection_made(self, transport: sthread.Protocol):
        super(DevlprReader, self).connection_made(transport)
        logging.info('Serial Port Opened\n')

    def handle_line(self, data: str):
        (topic, meat) = unwrap(data)
        for cb in self.read_callbacks[topic]:
            cb(meat)

    def connection_lost(self, exc: Exception):
        if exc:
            logging.error("Connection Lost : {}\n".format(exc))
        logging.info("Serial Port Closed\n")

def find_port() -> str:
    port_list = list_ports.comports()
    for port in port_list:
        if 'arduino' in port.description.lower():
            return port.device    
    return ""

def connect_to_arduino() -> serial.Serial:
    port = find_port()
    if port == "":
        logging.error("No Arduino Found")
        sys.exit(1)
    try:
        serif = serial.serial_for_url(port, baudrate=BAUD)
    except serial.SerialException as e:
        logging.error('Failed to open serial port {}: {}\n'.format(port, e))
        sys.exit(1)
    return serif

def init_serial():
    global serial_worker, devlpr_reader
    serif = connect_to_arduino()
    devlpr_reader = DevlprReader()
    serial_worker = sthread.ReaderThread(serif, DevlprReader)
    serial_worker.start()
    
def deinit_serial():
    global serial_worker, devlpr_reader
    if serial_worker is not None:
        serial_worker.stop()
    serial_worker = None
    devlpr_reader = None
    
def add_callback(topic, fn: Callable[[str], None]):
    if serial_worker is None or devlpr_reader is None:
        init_serial()
    if topic not in devlpr_reader.read_callbacks:
        devlpr_reader.read_callbacks[topic] = list()    
    devlpr_reader.read_callbacks[topic].append(fn)
    