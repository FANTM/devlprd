import os, sys, time
from threading import Thread
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from devlprd import *
from protocol import *

async def test_connect():
    print("Start")
    try:
        async with websockets.connect("ws://{}:{}".format(ADDRESS[0], ADDRESS[1])) as ws:
            await ws.send("{}{}{}".format(PacketType.SUBSCRIBE, DELIM, DataTopic.RAW_DATA_TOPIC))
            data = await ws.recv()
            print(data)
    except Exception:
        raise KeyboardInterrupt

async def run_all_tests():
    await test_connect()

if __name__ == "__main__":
    try:
        t: Thread = Thread(target=asyncio.new_event_loop().run_until_complete, args=[run_all_tests()])
        t.start()
        main()
    except KeyboardInterrupt:
        # t.join(timeout=1)
        exit()