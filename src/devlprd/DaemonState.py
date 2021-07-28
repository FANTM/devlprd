import asyncio
import logging
import threading
import collections as coll
import websockets.server

from typing import Callable, Deque, Dict, List, Union

class DaemonState:
    """Thread protected shared state for the Daemon. It manages all of the connections and data topics."""

    BUFFER_SIZE = 155  # Somewhat arbitrary, can be fine tuned to provide different results with data processing (e.g. changes response time vs smoothing).
    def __init__(self):
        from .protocol import DataTopic

        self.SUBS: Dict[str, List[websockets.server.WebSocketServerProtocol]] = dict()
        self.SERIAL_DATA: Dict[int, Deque[int]] = dict()
        self.SUBS_LOCK = threading.Lock()
        self.SERIAL_DATA_LOCK = threading.Lock()
        self.event_loop: asyncio.events.AbstractEventLoop = None
        self.callbacks: Dict[str, Callable[[int], Union[int, bool]]] = {
            DataTopic.RAW_DATA_TOPIC : self.peek_serial_data,
            DataTopic.FLEX_TOPIC     : self.flex_callback,
        }
        self.server: websockets.server.WebSocketServer = None

    def subscribe(self, websocket: websockets.server.WebSocketServerProtocol, topic: str) -> None:
        """Add a websocket to the list that should recv new data when available for a specified topic."""

        with self.SUBS_LOCK:
            try:
                if websocket not in self.SUBS[topic]:
                    self.SUBS[topic].append(websocket)
            except KeyError:
                self.SUBS[topic] = list()
                self.SUBS[topic].append(websocket)
    
    def pub(self, pin: int) -> None:
        """Publishes to all data topics. Each topic has a callback associated with it and that's how it generates the outbound data."""

        # attributes = [attr for attr in dir(DataTopic) if not attr.startswith('__')]  # https://stackoverflow.com/a/5970022
        for topic, cb in self.callbacks.items():
            asyncio.run_coroutine_threadsafe(self._pub(topic, pin, cb), loop=self.event_loop)

    async def _pub(self, topic: str, pin: int, callback: Callable[[int], Union[int, bool]]) -> None:
        """Uses a callback to generate data and then pushes that out to every websocket subscribed to the specified topic."""
        
        from .protocol import wrap_packet
        try:
            for sub in self.SUBS[topic]:
                try:
                    await sub.send(wrap_packet(topic, pin, callback(pin)))
                except:
                    pass
        except:
            pass

    def unsubscribe(self, websocket: websockets.server.WebSocketServerProtocol, topic: str) -> None:
        """Removes a websocket from the list of websockets that should get data from a topic."""

        try:
            with self.SUBS_LOCK:
                self.SUBS[topic].remove(websocket)
        except ValueError:
            logging.warning("Trying to unsubscribe w/o ever subscribing")

    def unsubscribe_all(self, websocket: websockets.server.WebSocketServerProtocol) -> None:
        """Removes a websocket from every topic it is subscribed to so it recvs no new data."""

        with self.SUBS_LOCK:
            print(self.SUBS)
            for subscribers in self.SUBS.values():
                try:
                    while websocket in subscribers:
                        subscribers.remove(websocket)
                except ValueError:
                    pass

    def enqueue_serial_data(self, pin: int, data: int) -> None:
        """FIFO adding of data to shared serial data buffer for us with callbacks using the raw data."""

        with self.SERIAL_DATA_LOCK:
            try:
                self.SERIAL_DATA[pin].appendleft(data)
            except KeyError:
                self.SERIAL_DATA[pin] = coll.deque(maxlen=self.BUFFER_SIZE)
                self.SERIAL_DATA[pin].appendleft(data)

    def dequeue_serial_data(self, pin: int) -> int:
        """FIFO removal of data from shared serial data buffer. Used with data processing that consumes raw data."""

        with self.SERIAL_DATA_LOCK:
            try:
                return self.SERIAL_DATA[pin].pop()
            except: 
                raise KeyError

    def peek_serial_data(self, pin: int) -> int:
        """View the last element added to shared serial buffer without actually consuming. 
        
        This is prefered if you need to use the data in many places.
        """

        with self.SERIAL_DATA_LOCK:
            try:
                return self.SERIAL_DATA[pin][len(self.SERIAL_DATA) - 1]
            except KeyError as e:
                logging.error("Entry not found")
                raise e
            except ValueError:
                logging.info("Buffer empty")
                return -1
            except IndexError as e:
                print(self.SERIAL_DATA)
                print(pin)
                print(len(self.SERIAL_DATA) - 1)
                print(self.SERIAL_DATA[pin])
                raise e

    def flex_callback(self, pin: int) -> bool:
        """Wrapper for mapping the flex topic to the filtering flex function."""
        
        from .filtering import flex_check
        return flex_check(self.peek_serial_data(pin))
