import logging
from enum import Enum
from typing import Tuple

class PacketType(Enum):
    SUBSCRIBE = "s"
    DATA = "d"
    UNSUBSCRIBE = "u"
    def __str__(self) -> str:
        return self.value

PROTOCOL = "|"  # Delimiter for messages 

# Package a message for sending using the agreed on protocol
def wrap(msg_type: PacketType, msg: str) -> str:
    return "{}{}{}".format(msg_type, PROTOCOL, msg)

# Unpackage a message into its command (type) and data
def unwrap(msg: str) -> Tuple[PacketType, str]:
    unwrapped = msg.split(PROTOCOL, maxsplit=1)
    if len(unwrapped) < 2:
        logging.warn("Invalid message")
        return ("", "")
    return (unwrapped[0], unwrapped[1])