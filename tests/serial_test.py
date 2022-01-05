import time, pytest, asyncio, logging
from ..src.devlprd.DaemonState import DaemonState
from ..src.devlprd import serif
from ..src.devlprd.config import BOARDS
from ..src.devlprd.daemon import shutdown

CURRENT_BOARD = BOARDS['DEVLPR']

logging.basicConfig(level=logging.INFO)
class TestSerial():
    
    @pytest.mark.asyncio
    def test_basic(self):
        TEST_SIZE = 15000
        DaemonState.BUFFER_SIZE = TEST_SIZE
        state: DaemonState = DaemonState(asyncio.get_event_loop(), CURRENT_BOARD)
        DEVLPR_SERIF = serif.DevlprSerif(CURRENT_BOARD)
        succ = DEVLPR_SERIF.init_serial(state)
        start = time.time()
        # Assumes pin 0
        logging.warning(state.SERIAL_DATA[0])
        while succ and len(state.SERIAL_DATA[0]) < TEST_SIZE:
            time.sleep(0.1)
        del state
        end = time.time()
        DEVLPR_SERIF.deinit_serial()
        time.sleep(0.5)
        logging.warning(f'DELTA: {end - start}')

if __name__ == "__main__":
    pytest.main()