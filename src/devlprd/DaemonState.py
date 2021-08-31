import asyncio
import logging
import threading
import collections as coll

from .protocol import wrap_packet,DataTopic
from typing import Callable, Deque, Dict, List, Union

class DaemonState:
    """Thread protected shared state for the Daemon. It manages all of the connections and data topics."""

    BUFFER_SIZE = 155  # Somewhat arbitrary, can be fine tuned to provide different results with data processing (e.g. changes response time vs smoothing).
    def __init__(self, event_loop):

        self.SUBS: Dict[str, List[websockets.server.WebSocketServerProtocol]] = dict()
        self.SERIAL_DATA: Dict[int, Deque[int]] = dict()
        self.SUBS_LOCK = threading.Lock()
        self.SERIAL_DATA_LOCK = threading.Lock()
        self.event_loop = event_loop

    def subscribe(self, websocket: wss.WebSocketServerProtocol, topic: str) -> None:
        """Add a websocket to the list that should recv new data when available for a specified topic."""

        with self.SUBS_LOCK:
            try:
                if websocket not in self.SUBS[topic]:
                    self.SUBS[topic].append(websocket)
            except KeyError:
                self.SUBS[topic] = list()
                self.SUBS[topic].append(websocket)

    async def _pub_int(self, topic: str, pin: int, payload: int) -> None:
        """Coroutine that pushes given integer payload to every websocket subscribed to the specified topic."""

        try:
            for sub in self.SUBS[topic]:
                try:
                    await sub.send(wrap_packet(topic, pin, payload))
                except:
                    pass
        except:
            pass

    async def _pub_bool(self, topic: str, pin: int, payload: bool) -> None:
        """Coroutine that pushes given boolean payload to every websocket subscribed to the specified topic."""

        try:
            for sub in self.SUBS[topic]:
                try:
                    await sub.send(wrap_packet(topic, pin, paylod))
                except:
                    pass
        except:
            pass

    def unsubscribe(self, websocket: wss.WebSocketServerProtocol, topic: str) -> None:
        """Removes a websocket from the list of websockets that should get data from a topic."""

        try:
            with self.SUBS_LOCK:
                self.SUBS[topic].remove(websocket)
        except ValueError:
            logging.warning("Trying to unsubscribe w/o ever subscribing")

    def unsubscribe_all(self, websocket: wss.WebSocketServerProtocol) -> None:
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
        """FIFO adding of data to shared serial data buffer and queuing up publishing."""

        with self.SERIAL_DATA_LOCK:
            try:
                self.SERIAL_DATA[pin].appendleft(data)
            except KeyError:
                self.SERIAL_DATA[pin] = coll.deque(maxlen=self.BUFFER_SIZE)
                self.SERIAL_DATA[pin].appendleft(data)
        # we need to make sure each processed chunk of data is published in lock-step with receipt of raw
        # might need to consider a Queue if publishing gets out of order
        asyncio.run_coroutine_threadsafe(self._pub_int(DataTopic.RAW_DATA_TOPIC, pin, data), loop=self.event_loop)
