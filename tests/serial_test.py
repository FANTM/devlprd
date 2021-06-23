import os, sys, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from serif import *

def serial_basic_test():
    init_serial()
    i = 0
    while i < 10:
        if 0 in SERIAL_DATA:
            print(SERIAL_DATA[0][0])
        else:
            print("Nothing yet")
        i += 1
        time.sleep(1)
    deinit_serial()
    
def run_all_tests():
    serial_basic_test()

if __name__ == "__main__":
    run_all_tests()
