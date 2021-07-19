import asyncio
import time
import unittest
import websockets
import threading
import ServerWrapper
import os, sys
sys.path.insert(0, os.path.join('..', 'devlprd'))
import devlprd as d
import protocol 

class TestWebsocket(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.test_server = ServerWrapper.TestServer()
        self.test_server_thread: threading.Thread = threading.Thread(target=self.test_server.start)
        time.sleep(1)
        self.test_server_thread.start()
    
    async def asyncSetUp(self) -> None:
        pass

    def tearDown(self) -> None:
        self.test_server.stop()
        self.test_server_thread.join()

    async def test_connect(self) -> None:
        try:
            async with websockets.connect("ws://{}:{}".format(d.ADDRESS[0], d.ADDRESS[1])) as ws:
                None
        except:
            self.fail("Couldn't connect")
            
    async def test_pubsub(self):
        async with websockets.connect("ws://{}:{}".format(d.ADDRESS[0], d.ADDRESS[1])) as ws:
            await ws.send("{}{}{}".format(protocol.PacketType.SUBSCRIBE, protocol.DELIM, self.test_server.TEST_TOPIC))
            self.test_server.state.pub(0)
            try:
                data = await asyncio.wait_for(ws.recv(), 1)
            except asyncio.TimeoutError:
                self.fail("Timed out on recv")
            broken_packet = data.split(protocol.DELIM, maxsplit=3)
            self.assertEqual(len(broken_packet), 3)
            (topic, pin, meat) = broken_packet
            self.assertEqual(topic, self.test_server.TEST_TOPIC)
            self.assertEqual(pin, "0")
            self.assertEqual(meat, "1")

if __name__ == "__main__":
    unittest.main()