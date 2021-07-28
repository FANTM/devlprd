import asyncio
from ..src.devlprd.daemon import state, shutdown, startup

class MockServer:
    def __init__(self) -> None:
        self.TEST_TOPIC = "test"
        self.state = state

    def testDataGen(self, unused: int) -> int:
        return 1

    def start(self):
        self.state.callbacks[self.TEST_TOPIC] = self.testDataGen
        asyncio.run(startup())
    
    def stop(self):
        shutdown()