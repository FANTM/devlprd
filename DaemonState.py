from typing import List, Dict, Deque
from websockets import server
from threading import Lock
import logging
from collections import deque
from protocol import wrap_packet

## Thread protected shared state for the Daemon. It manages all of the connections and data topics
class DaemonState:
    BUFFER_SIZE = 155
    def __init__(self):
        self.SUBS: Dict[str, List[server.WebSocketServerProtocol]] = dict()
        self.SERIAL_DATA: Dict[int, Deque[int]] = dict()
        self.SUBS_LOCK = Lock()
        self.SERIAL_DATA_LOCK = Lock()

    def subscribe(self, websocket: server.WebSocketServerProtocol, topic: str) -> None:
        with self.SUBS_LOCK:
            try:
                self.SUBS[topic].append(websocket)
            except KeyError:
                self.SUBS[topic] = list()
                self.SUBS[topic].append(websocket)
    
    async def pub(self, topic: str, pin: int, data: str) -> None:
        try:
            for sub in self.SUBS[topic]:
                await sub.send(wrap_packet(topic, pin, data))
        except:
            pass

    def unsubscribe(self, websocket: server.WebSocketServerProtocol, topic: str) -> None:
        try:
            with self.SUBS_LOCK:
                self.SUBS[topic].remove(websocket)
        except ValueError:
            logging.warning("Trying to unsubscribe w/o ever subscribing")

    def unsubscribe_all(self, websocket: server.WebSocketServerProtocol) -> None:
        with self.SUBS_LOCK:
            for subscribers in self.SUBS.values():
                try:
                    subscribers.remove(websocket)
                except ValueError:
                    pass
    
    def push_serial_data(self, pin: int, data: int) -> None:
        with self.SERIAL_DATA_LOCK:
            try:
                self.SERIAL_DATA[pin].appendleft(data)
            except KeyError:
                self.SERIAL_DATA[pin] = deque(maxlen=self.BUFFER_SIZE)
                self.SERIAL_DATA[pin].appendleft(data)

    def pop_serial_data(self, pin: int) -> int:
        with self.SERIAL_DATA_LOCK:
            try:
                return self.SERIAL_DATA[pin].pop()
            except: 
                raise KeyError