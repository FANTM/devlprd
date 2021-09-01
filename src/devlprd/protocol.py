import logging
import typing
import struct

import websockets.typing as ws_typing

class DaemonSocket:

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.remote_address = writer.get_extra_info('peername')

    def get_remote_address(self):
        return self.remote_address

    def closed(self):
        return self.writer.is_closing()

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()

    async def send(self, msg):
        # make sure we're not closed before trying to write
        if self.closed():
            return
        msg += "\n"
        self.writer.write(msg.encode())
        await self.writer.drain()

    async def recv(self):
        # make sure we're not closed before trying to read
        if self.closed():
            return ''
        msg = await self.reader.readline()
        return msg.decode().strip()

class DataFormatException(Exception):
    """Exception thrown when protocol.py conversions fail."""

    pass

class PacketType():
    """Shorthands for the packet types the daemon sends/recvs.
    
    PacketTypes must be 1 character to avoid overlap with DataTopic.
    """

    SUBSCRIBE = "s"
    DATA = "d"
    UNSUBSCRIBE = "u"   # TODO

class DataTopic():
    """Shorthands for each of the supported topics.
    
    All DataTopics should be 2 characters to avoid overlap with PacketType.
     """
    
    RAW_DATA_TOPIC = "ra"
    FLEX_TOPIC     = "fl"
    PEAK_TO_PEAK_TOPIC = "pp"  # TODO
    PEAK_AMP_TOPIC  = "pa"     # TODO
    WINDOW_AVG_TOPIC = "wa"    # TODO
    NOTCH_60_TOPIC = "60"      # TODO
    NOTCH_50_TOPIC = "50"      # TODO

DELIM = "|"  # Agreed upon protocol delimiter with daemon/plugin

def wrap_packet(msg_type: str, pin: int, msg: int) -> str:
    """Packages the messages in the way that the daemon expects."""

    return "{}{}{}{}{}".format(msg_type, DELIM, str(pin), DELIM, str(msg))


def unwrap_packet(msg: ws_typing.Data) -> typing.Tuple[str, str]:
    """Extracts the data, pin and topic from the incoming message from the daemon."""

    try:
        unwrapped = str(msg).split(DELIM, maxsplit=1)
    except TypeError:
        logging.warning("Invalid Message Type")
        raise DataFormatException
    
    try:
        return (unwrapped[0], unwrapped[1])
    except IndexError:
        logging.warning("Invalid Message - msg: {!r}, unwrapped: {}".format(msg, unwrapped))
        raise DataFormatException

def unpack_serial(byte_array: bytes) -> typing.Tuple[int, int]:
    """Takes an incoming serial, bitpacked message from the DEVLPR and formats it for the daemon."""
    if len(byte_array) != 3:
        logging.warning("Invalid Message - {}".format(byte_array))
        raise DataFormatException
    try:
        # create a temporary bytearray to unpack our weird protocol
        # bit packing in 3 bytes for emg (16 bit) and pin (4 bit) follows:
        # eeee eee0
        # eeee eee0
        # eepp pp00
        tmp = bytearray([0,0,0])
        tmp[0] = byte_array[0] | (byte_array[1] >> 7)
        tmp[1] = ((byte_array[1] << 1) & 0xFF) | (byte_array[2] >> 6)
        tmp[2] = (byte_array[2] >> 2) & 0x0F
        data,pin = struct.unpack('>hB', tmp)
    except IndexError:
        logging.warning("Invalid Message")
        raise DataFormatException
    return (pin, data)
