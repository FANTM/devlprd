import datetime as DT
import math
from pydevlpr_protocol import DataTopic

BUTTERWORTH = {
    DataTopic.NOTCH_50_TOPIC: [
        [0.95654323, -1.82035157, 0.95654323, 1.0, -1.84458768, 0.9536256],
        [1.0, -1.90305207, 1.0, 1.0, -1.87701816, 0.95947072]
    ],
    DataTopic.NOTCH_60_TOPIC: [
        [0.95654323, -1.77962093, 0.95654323, 1.0, -1.80093517, 0.95415195], 
        []
    ]
}

prevMicros = 0
prevValue = math.inf  # By making this infinite we avoid a false positive on the first run through.

def micros() -> int:
    """Gets a microsecond timestamp in the range of [0, 6 * 10^8)."""

    time = DT.datetime.now()
    timestr = time.strftime('%S:%f')
    sec,micro = timestr.split(':')
    return int(sec) * 1e6 + int(micro)
    
def flex_check(value: int, thresholdMult: float = 1.5, cooldown: int = 400000) -> bool:
    """Determine if a flex has occurred.

    Uses a variable threshold and cooldown to both check if a flex appeared and to debounce the result.
    You will likely want to calibrate it for a specific application, but the default values are a good starting point.
    """

    global prevMicros, prevValue
    currMicros = micros()
    if currMicros < prevMicros:
        # We rolled over, micro stamp only goes up to 6 * 10^8 - 1
        delta = currMicros + (1e8 * 6) - prevMicros
    else:
        delta = currMicros - prevMicros
    
    # Check if it has been long enough for another threshold check
    if delta >= cooldown:
        # Only calculate the threshold when we know we need to check it
        threshold = thresholdMult * prevValue
        if value >= threshold: # Rising edge detection
            prevValue = value
            prevMicros = currMicros
            return True
    prevValue = value
    return False