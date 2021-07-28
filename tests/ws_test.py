import asyncio
import time
import pytest
import websockets
import threading
from .ServerWrapper import MockServer
from ..src.devlprd.protocol import PacketType, DELIM 
from ..src.devlprd.daemon import ADDRESS

@pytest.fixture(autouse=True)
def server() -> MockServer:
    test_server = MockServer()
    test_server_thread: threading.Thread = threading.Thread(target=test_server.start)
    test_server_thread.start()
    while test_server.state.server is None:
        pass
    yield test_server
    test_server.stop()
    test_server_thread.join()

@pytest.mark.asyncio
async def test_connect() -> None:
    try:
        async with websockets.connect("ws://{}:{}".format(ADDRESS[0], ADDRESS[1])) as ws:
            pass
    except Exception as e:
        pytest.fail(e)
    
async def block_until_subscribed(test_server) -> None:
    while test_server.TEST_TOPIC not in test_server.state.SUBS.keys():
        pass

@pytest.mark.asyncio
async def test_pubsub(server):
    async with websockets.connect("ws://{}:{}".format(ADDRESS[0], ADDRESS[1])) as ws:
        await ws.send("{}{}{}".format(PacketType.SUBSCRIBE, DELIM, server.TEST_TOPIC))
        try:
            await asyncio.wait_for(block_until_subscribed(server), 2)
        except Exception as e:
            pytest.fail(e)
        server.state.pub(0)
        try:
            data = await asyncio.wait_for(ws.recv(), 1)
        except asyncio.TimeoutError:
            pytest.fail("Timed out on recv")
        broken_packet = data.split(DELIM, maxsplit=3)
        assert len(broken_packet) == 3
        (topic, pin, meat) = broken_packet
        assert topic == server.TEST_TOPIC
        assert pin == "0"
        assert meat == "1"

if __name__ == "__main__":
    pytest.main()
