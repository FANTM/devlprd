import unittest
import os, sys
sys.path.insert(0, os.path.join('..', 'devlprd'))
from protocol import DataTopic, wrap_packet, unwrap_packet, unpack_serial, DataFormatException

class TestWrap(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()
    
    def test_nominal(self):
        msg_type = DataTopic.RAW_DATA_TOPIC
        pin = 0
        msg = 100
        packet = wrap_packet(msg_type, pin, msg)
        self.assertEqual("ra|0|100", packet)

class TestUnwrap(unittest.TestCase):
    def test_nominal(self):
        msg = "s|ra"
        try:
            (msg_type, content) = unwrap_packet(msg)
        except DataFormatException:
            self.fail("Unwrap failed")
        self.assertEqual(msg_type, "s")
        self.assertEqual(content, "ra")

class TestUnpack(unittest.TestCase):
    def test_nominal(self):
        byte_array = [0x3B, 0xEF]
        try:
            (pin, data) = unpack_serial(byte_array)
        except DataFormatException:
            self.fail("Unpack failed")
        self.assertEqual(pin, 3)
        self.assertEqual(data, 0x0BEF)

if __name__ == "__main__":
    unittest.main()