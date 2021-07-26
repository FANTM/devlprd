import os, sys, time, unittest
sys.path.insert(0, os.path.join('..', 'devlprd'))
from DaemonState import DaemonState
import serif

STATE: DaemonState = DaemonState()

class TestSerial(unittest.TestCase):
    def test_basic(self):
        DEVLPR_SERIF = serif.DevlprSerif()
        DEVLPR_SERIF.init_serial(STATE)
        i = 0
        while i < 500:
            for pin in STATE.SERIAL_DATA:
                print(STATE.SERIAL_DATA)
                # print("PIN: {}, DATA: {}".format(pin, STATE.peek_serial_data(pin)))
            i += 1
            time.sleep(0.01)
        DEVLPR_SERIF.deinit_serial()

if __name__ == "__main__":
    unittest.main()