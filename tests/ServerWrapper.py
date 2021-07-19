import os, sys
sys.path.insert(0, os.path.join('..', 'devlprd'))
import devlprd as d

class TestServer:
    def __init__(self) -> None:
        self.TEST_TOPIC = "test"
        self.state = d.state

    def testDataGen(self, unused: int) -> int:
        return 1

    def start(self):
        self.state.callbacks[self.TEST_TOPIC] = self.testDataGen
        d.main()
    
    def stop(self):
        d.shutdown()