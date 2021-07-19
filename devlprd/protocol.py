import logging
import typing

import websockets.typing as ws_typing

class DataFormatException(Exception):
    pass

# PacketTypes must be 1 character to avoid overlap with DataTopic
class PacketType():
    SUBSCRIBE = "s"
    DATA = "d"
    UNSUBSCRIBE = "u"

# All DataTopics should be 2 characters to avoid overlap with PacketType
class DataTopic():
    RAW_DATA_TOPIC = "ra"
    FLEX_TOPIC     = "fl"
    PEAK_TO_PEAK_TOPIC = "pp"
    PEAK_AMP_TOPIC  = "pa"
    WINDOW_AVG_TOPIC = "wa"
    NOTCH_60_TOPIC = "60"
    NOTCH_50_TOPIC = "50"

DELIM = "|"  # Agreed upon protocol delimiter with daemon

# Packages the messages in the way that the daemon expects
def wrap_packet(msg_type: str, pin: int, msg: int) -> str:
    return "{}{}{}{}{}".format(msg_type, DELIM, str(pin), DELIM, str(msg))

# Extracts the data, pin and topic from the incoming message from the daemon.
def unwrap_packet(msg: ws_typing.Data) -> typing.Tuple[str, str]:
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
    try:        
        pin = (byte_array[0] >> 4) & 0x0F
        data = ((byte_array[0] & 0x0F) << 8) | byte_array[1]
    except IndexError:
        logging.warning("Invalid Message")
        raise DataFormatException
    return (pin, data)
