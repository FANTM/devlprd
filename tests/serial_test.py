import time, pytest, asyncio, logging
from ..src.devlprd.DaemonState import DaemonState
from ..src.devlprd import serif
from ..src.devlprd.config import BOARDS
from ..src.devlprd.daemon import shutdown

state: DaemonState = DaemonState(asyncio.get_event_loop(), BOARDS['Neuron'])
logging.basicConfig(level=logging.INFO)
class TestSerial():
    def test_basic(self):
        DEVLPR_SERIF = serif.DevlprSerif(BOARDS['Neuron'])
        DEVLPR_SERIF.init_serial(state)
        start = time.time()
        i = 0
        TEST_SIZE = 15000
        # Assumes pin 0
        while len(state.SERIAL_DATA[0]) < TEST_SIZE:
            pass
            # for pin in STATE.SERIAL_DATA:
            # logging.error(state.SERIAL_DATA)
            # logging.error(len(state.SERIAL_DATA[0]))
                # logging.info(STATE.SERIAL_DATA)
                # logging.warning("PIN: {}, DATA: {}".format(pin, STATE.SERIAL_DATA[pin]))
            i += 1
        end = time.time()
        shutdown()
        logging.warning(f'DELTA: {end - start}')
        pytest.fail("No reason")

if __name__ == "__main__":
    pytest.main()