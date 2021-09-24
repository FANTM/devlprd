import asyncio
import time
import pytest
import threading

from .ServerWrapper import MockServer, MockClient
from ..src.devlprd.config import CONFIG

BAILOUT = True

@pytest.fixture(autouse=True)
def server() -> MockServer:
    if BAILOUT:
        yield MockServer()
    else:
        test_server = MockServer()
        test_server_thread: threading.Thread = threading.Thread(target=test_server.start)
        test_server_thread.start()
        yield test_server
        test_server.stop()
        test_server_thread.join()

@pytest.mark.asyncio
async def test_connect(server) -> None:
    if BAILOUT:
        return
    ADDRESS = CONFIG["ADDRESS"]
    client = MockClient()
    try:
        await client.try_connect(ADDRESS[0], ADDRESS[1])
    except Exception as e:
        pytest.fail(e)

async def check_subscribed(test_server, sleep_sec) -> None:
    await asyncio.sleep(2)
    return test_server.TEST_TOPIC in test_server.state().SUBS

@pytest.mark.asyncio
async def test_pubsub(server):
    if BAILOUT:
        return
    ADDRESS = CONFIG["ADDRESS"]
    client = MockClient()
    try:
        await client.try_connect(ADDRESS[0], ADDRESS[1])
    except Exception as e:
        pytest.fail(e)
    await client.try_sub(server.TEST_TOPIC)
    sub_success = await check_subscribed(server, 2)
    if not sub_success:
        pytest.fail("Subscribe failed\n{0}".format(server.state().SUBS))
    server.try_pub_data(0, 1)
    data = await client.try_recv()
    broken_packet = client.try_process_data(data)
    assert len(broken_packet) == 3
    (topic, pin, meat) = broken_packet
    assert topic == server.TEST_TOPIC
    assert pin == "0"
    assert meat == "1"

if __name__ == "__main__":
    pytest.main()
