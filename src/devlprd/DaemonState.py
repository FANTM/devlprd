import asyncio
import logging
import threading
import collections as coll
from .config import Board
from .filtering import ButterworthFilter, BUTTER8_45_55_NOTCH, BUTTER8_55_65_NOTCH
from pydevlpr_protocol import wrap_packet, DataTopic, DaemonSocket
from typing import Deque, Dict, List

class DaemonState:
    """Thread protected shared state for the Daemon. It manages all of the connections and data topics."""

    BUFFER_SIZE = 64  # Somewhat arbitrary, can be fine tuned to provide different results with data processing (e.g. changes response time vs smoothing).
    def __init__(self, event_loop, board: Board):
        self.PIN_NUMS = list(range(0, board['NUM PINS']))
        self.SUBS: Dict[str, List[DaemonSocket]] = dict()
        self.SERIAL_DATA: Dict[int, Deque[int]] = dict()
        self.SERIAL_DATA_RUNNING_SUMS: Dict[int, float] = dict() # for window avg
        self.SUBS_LOCK = threading.Lock()
        self.SERIAL_DATA_LOCK = threading.Lock()
        self.event_loop = event_loop
        self.init_butterworth_filters()
        self.init_data_buffers()

    def init_butterworth_filters(self):
        # we need a filter object for each pin
        # they shouldn't take up too much space, so just make them all ahead
        self.BUTTER60_FILTS = dict()
        self.BUTTER50_FILTS = dict()
        # go through all possible pins and create a new one
        for pin in self.PIN_NUMS:
            self.BUTTER60_FILTS[pin] = ButterworthFilter(BUTTER8_55_65_NOTCH)
            self.BUTTER50_FILTS[pin] = ButterworthFilter(BUTTER8_45_55_NOTCH)

    def init_data_buffers(self):
        # no need to save space, just make buffer objects ahead
        for pin in self.PIN_NUMS:
            # just create the deque and throw an initial 0 in there for now
            self.SERIAL_DATA[pin] = coll.deque(maxlen=self.BUFFER_SIZE)
            self.SERIAL_DATA[pin].appendleft(0)
            self.SERIAL_DATA_RUNNING_SUMS[pin] = 0.0

    def subscribe(self, dsock: DaemonSocket, topic: str) -> None:
        """Add a socket to the list that should recv new data when available for a specified topic."""

        with self.SUBS_LOCK:
            try:
                if dsock not in self.SUBS[topic]:
                    self.SUBS[topic].append(dsock)
            except KeyError:
                self.SUBS[topic] = list()
                self.SUBS[topic].append(dsock)

    async def _pub_int(self, topic: str, pin: int, payload: int) -> None:
        """Coroutine that pushes given integer payload to every socket subscribed to the specified topic."""

        try:
            for sub in self.SUBS[topic]:
                try:
                    await sub.send(wrap_packet(topic, pin, payload))
                except:
                    pass
        except:
            pass

    async def _pub_float(self, topic: str, pin: int, payload: float) -> None:
        """Coroutine that pushes given floating point payload to every socket subscribed to the specified topic."""

        # NOTE should we really round the float here? it's not "real" precision anyway
        try:
            if len(self.SUBS[topic]) > 0:
                payload = round(payload, 4)
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
                    await sub.send(wrap_packet(topic, pin, payload))
                except:
                    pass
        except:
            pass

    def unsubscribe(self, dsock: DaemonSocket, topic: str) -> None:
        """Removes a socket from the list of sockets that should get data from a topic."""

        try:
            with self.SUBS_LOCK:
                self.SUBS[topic].remove(dsock)
        except ValueError:
            logging.warning("Trying to unsubscribe w/o ever subscribing")

    def unsubscribe_all(self, dsock: DaemonSocket) -> None:
        """Removes a socket from every topic it is subscribed to so it recvs no new data."""

        with self.SUBS_LOCK:
            print(self.SUBS)
            for subscribers in self.SUBS.values():
                try:
                    while dsock in subscribers:
                        subscribers.remove(dsock)
                except ValueError:
                    pass

    def enqueue_serial_data(self, pin: int, data: int) -> None:
        """FIFO adding of data to shared serial data buffer and queuing up publishing."""
        
        # we will want to calculate the window average for filtering etc
        buf_avg = 0.0
        data_centered = 0.0
        data_filt60 = 0.0
        data_filt50 = 0.0
        with self.SERIAL_DATA_LOCK:
            # before buffering, we should efficiently update the running sum
            # outgoing value is on the right
            new_sum = self.SERIAL_DATA_RUNNING_SUMS[pin] - self.SERIAL_DATA[pin][-1] + data
            self.SERIAL_DATA_RUNNING_SUMS[pin] = new_sum
            # and we can calculate the buffer average from the running sum
            buf_avg = new_sum / DaemonState.BUFFER_SIZE
            # now we can push out the old value
            self.SERIAL_DATA[pin].appendleft(data)
            # for filtering, we need to "center" the data (use the buffer average)
            # NOTE because of the state maintained by IIR filters, we always need to do the
            # NOTE filter calculation regardless of subscription - no breaks in the data
            data_centered = data - buf_avg
            data_filt60 = self.BUTTER60_FILTS[pin].next_sample(data_centered)
            data_filt50 = self.BUTTER50_FILTS[pin].next_sample(data_centered)
        # we need to make sure each processed chunk of data is published in lock-step with receipt of raw
        # might need to consider a Queue if publishing gets out of order   
        asyncio.run_coroutine_threadsafe(self._pub_int(DataTopic.RAW_DATA_TOPIC, pin, data), loop=self.event_loop)
        asyncio.run_coroutine_threadsafe(self._pub_float(DataTopic.NOTCH_60_TOPIC, pin, data_filt60), loop=self.event_loop)
        asyncio.run_coroutine_threadsafe(self._pub_float(DataTopic.NOTCH_50_TOPIC, pin, data_filt50), loop=self.event_loop)
