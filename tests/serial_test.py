import time, pytest, asyncio, logging
from ..src.devlprd.DaemonState import DaemonState
from ..src.devlprd import serif
from ..src.devlprd.config import BOARDS

STATE: DaemonState = DaemonState(asyncio.get_event_loop(), BOARDS['DEVLPR'])
logging.basicConfig(level=logging.INFO)
class TestSerial():
    def test_basic(self):
        DEVLPR_SERIF = serif.DevlprSerif(BOARDS['DEVLPR'])
        DEVLPR_SERIF.init_serial(STATE)
        i = 0
        while i < 500:
            for pin in STATE.SERIAL_DATA:
                # logging.info(STATE.SERIAL_DATA)
                logging.info("PIN: {}, DATA: {}".format(pin, STATE.SERIAL_DATA[pin]))
            i += 1
            time.sleep(0.01)
        DEVLPR_SERIF.deinit_serial()

if __name__ == "__main__":
    pytest.main()