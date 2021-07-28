import time

import pytest

from ..src.devlprd.filtering import flex_check


class TestFiltering():
    def test_flex(self):
        one_sec = 1e6  # uS for 1 second
        thresh = 1.5
        flex = flex_check(10, thresh, one_sec) 
        assert not flex  # Don't trigger on the first value, establishes baseline
        flex = flex_check(20, thresh, one_sec)
        assert flex  # 20 > 1.5 * 10 so we expect a flex
        time.sleep(1.1)  # Just needs to be > 1s
        flex = flex_check(31, thresh, one_sec)
        assert flex
        time.sleep(0.9) # Wait <1s to make sure we debounce
        flex = flex_check(61, thresh, one_sec)
        assert not flex  # Hasn't been long enough, no flex even though value is larger

if __name__ == "__main__":
    pytest.main()
        