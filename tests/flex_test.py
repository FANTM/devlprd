import unittest, os, sys, time
sys.path.insert(0, os.path.join('..', 'devlprd'))
import filtering

class FilteringTest(unittest.TestCase):
    
    def test_flex(self):
        one_sec = 1e6  # uS for 1 second
        thresh = 1.5
        flex = filtering.flex_check(10, thresh, one_sec) 
        self.assertFalse(flex)  # Don't trigger on the first value, establishes baseline
        flex = filtering.flex_check(20, thresh, one_sec)
        self.assertTrue(flex)  # 20 > 1.5 * 10 so we expect a flex
        time.sleep(1.1)  # Just needs to be > 1s
        flex = filtering.flex_check(31, thresh, one_sec)
        self.assertTrue(flex)
        time.sleep(0.9) # Wait <1s to make sure we debounce
        flex = filtering.flex_check(61, thresh, one_sec)
        self.assertFalse(flex)  # Hasn't been long enough, no flex even though value is larger

if __name__ == "__main__":
    unittest.main()
        