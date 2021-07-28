import os, sys
import pytest
from ..src.devlprd.protocol import DataTopic, wrap_packet, unwrap_packet, unpack_serial, DataFormatException

class TestWrap():
    def test_nominal(self):
        msg_type = DataTopic.RAW_DATA_TOPIC
        pin = 0
        msg = 100
        packet = wrap_packet(msg_type, pin, msg)
        assert "ra|0|100" == packet

class TestUnwrap():
    def test_nominal(self):
        msg = "s|ra"
        try:
            (msg_type, content) = unwrap_packet(msg)
        except DataFormatException:
            pytest.fail("Unwrap failed")
        assert msg_type == "s"
        assert content == "ra"

class TestUnpack():
    def test_nominal(self):
        byte_array = [0x3B, 0xEF]
        try:
            (pin, data) = unpack_serial(byte_array)
        except DataFormatException:
            pytest.fail("Unpack failed")
        assert pin == 3
        assert data == 0x0BEF

if __name__ == "__main__":
    pytest.main()