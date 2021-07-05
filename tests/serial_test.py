import os, sys, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from serif import *

STATE: DaemonState = DaemonState()

def serial_basic_test():
    init_serial(STATE, None)
    i = 0
    while i < 10:
        
        for pin in STATE.SERIAL_DATA:
            print("PIN: {}, DATA: {}".format(pin, STATE.peek_serial_data(pin)))
        i += 1
        time.sleep(1)
    deinit_serial()
    
def run_all_tests():
    serial_basic_test()

if __name__ == "__main__":
    run_all_tests()
