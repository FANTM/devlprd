import asyncio
from ..src.devlprd.daemon import shutdown, startup, _get_state
from pydevlpr_protocol import DaemonSocket, PacketType, unwrap_packet, wrap_packet

class MockServer:
    def __init__(self) -> None:
        self.TEST_TOPIC = "test"

    def try_pub_data(self, pin, value):
        state = self.state()
        asyncio.run_coroutine_threadsafe(state._pub_int(self.TEST_TOPIC, pin, value), loop=state.event_loop)

    def start(self):
        asyncio.run(startup())
    
    def stop(self):
        shutdown()

    def state(self):
        return _get_state()

class MockClient:
    def __init__(self):
        pass

    async def try_connect(self, host, port):
        reader, writer = await asyncio.open_connection(host, port)
        self.connection = DaemonSocket(reader, writer)

    async def try_sub(self, topic):
        self.connection.send(wrap_packet(PacketType.SUBSCRIBE, topic))
    
    async def try_recv(self):
        return self.connection.recv()

    def try_process_data(self, data):
        packet = unwrap_packet(data)
