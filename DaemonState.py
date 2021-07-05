from typing import List, Dict
from websockets import server
from threading import Lock
import logging
from protocol import wrap_packet

class DaemonState:
    def __init__(self):
        self.SUBS: Dict[str, List[server.WebSocketServerProtocol]] = dict()
        self.SUBS_LOCK = Lock()

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
