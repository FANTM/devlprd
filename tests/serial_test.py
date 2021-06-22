import os, sys, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from serif import *

def serial_basic_test():
    init_serial()
    time.sleep(10)
    deinit_serial()
    
def run_all_tests():
    serial_basic_test()

if __name__ == "__main__":
    run_all_tests()
