import asyncio
import logging
import threading
import collections as coll
from typing import Callable, Deque, Dict, List, Union
import websockets.server
import filtering
import protocol


## Thread protected shared state for the Daemon. It manages all of the connections and data topics
class DaemonState:
    BUFFER_SIZE = 155
    def __init__(self):
        self.SUBS: Dict[str, List[websockets.server.WebSocketServerProtocol]] = dict()
        self.SERIAL_DATA: Dict[int, Deque[int]] = dict()
        self.SUBS_LOCK = threading.Lock()
        self.SERIAL_DATA_LOCK = threading.Lock()
        self.event_loop: asyncio.events.AbstractEventLoop = None
        self.callbacks: Dict[str, Callable[[int], Union[int, bool]]] = {
            protocol.DataTopic.RAW_DATA_TOPIC : self.peek_serial_data,
            protocol.DataTopic.FLEX_TOPIC     : self.flex_callback,
        }
        self.server: websockets.server.WebSocketServer = None

    def subscribe(self, websocket: websockets.server.WebSocketServerProtocol, topic: str) -> None:
        with self.SUBS_LOCK:
            try:
                if websocket not in self.SUBS[topic]:
                    self.SUBS[topic].append(websocket)
            except KeyError:
                self.SUBS[topic] = list()
                self.SUBS[topic].append(websocket)
    
    def pub(self, pin: int) -> None:
        # attributes = [attr for attr in dir(DataTopic) if not attr.startswith('__')]  # https://stackoverflow.com/a/5970022
        for topic, cb in self.callbacks.items():
            asyncio.run_coroutine_threadsafe(self._pub(topic, pin, cb), loop=self.event_loop)

    async def _pub(self, topic: str, pin: int, callback: Callable[[int], Union[int, bool]]) -> None:
        try:
            for sub in self.SUBS[topic]:
                await sub.send(protocol.wrap_packet(topic, pin, callback(pin)))
        except:
            pass

    def unsubscribe(self, websocket: websockets.server.WebSocketServerProtocol, topic: str) -> None:
        try:
            with self.SUBS_LOCK:
                self.SUBS[topic].remove(websocket)
        except ValueError:
            logging.warning("Trying to unsubscribe w/o ever subscribing")

    def unsubscribe_all(self, websocket: websockets.server.WebSocketServerProtocol) -> None:
        with self.SUBS_LOCK:
            print(self.SUBS)
            for subscribers in self.SUBS.values():
                try:
                    while websocket in subscribers:
                        subscribers.remove(websocket)
                except ValueError:
                    pass

    def push_serial_data(self, pin: int, data: int) -> None:
        with self.SERIAL_DATA_LOCK:
            try:
                self.SERIAL_DATA[pin].appendleft(data)
            except KeyError:
                self.SERIAL_DATA[pin] = coll.deque(maxlen=self.BUFFER_SIZE)
                self.SERIAL_DATA[pin].appendleft(data)

    def pop_serial_data(self, pin: int) -> int:
        with self.SERIAL_DATA_LOCK:
            try:
                return self.SERIAL_DATA[pin].pop()
            except: 
                raise KeyError

    def peek_serial_data(self, pin) -> int:
        with self.SERIAL_DATA_LOCK:
            try:
                return self.SERIAL_DATA[pin][len(self.SERIAL_DATA) - 1]
            except KeyError as e:
                logging.error("Entry not found")
                raise e
            except ValueError:
                logging.info("Buffer empty")
                return -1
    
    def flex_callback(self, pin: int) -> bool:
        return filtering.flex_check(self.peek_serial_data(pin))
