import logging
from typing import Tuple

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
def wrap_packet(msg_type: str, pin: int, msg: str) -> str:
    return "{}{}{}{}{}".format(msg_type, DELIM, str(pin), DELIM, msg)

# Extracts the data, pin and topic from the incoming message from the daemon.
def unwrap_packet(msg: str) -> Tuple[str, str]:
    unwrapped = msg.split(DELIM, maxsplit=1)
    if len(unwrapped) != 2:
        logging.warning("Invalid Message - msg: {}, unwrapped: {}".format(msg, unwrapped))
        raise DataFormatException
    return (unwrapped[0], unwrapped[1])

def unpack_serial(byte_array: bytes) -> Tuple[int, str]:
    if len(byte_array) != 2:
        logging.warning("Invalid Message")
        raise DataFormatException
    pin = (byte_array[0] >> 4) & 0x0F
    data = ((byte_array[0] & 0x0F) << 8) | byte_array[1]
    return (pin, data)
