import pytest  # NOQA
from ctypes import c_bool
import time
from random import randint
from pyvisainstrument import KeysightDAQ
from pyvisainstrument.testsuite import DummyDAQ


class TestKeysightDAQ:

    def setup_class(self):
        instAddr = "TCPIP::{:s}::{:d}::SOCKET".format('localhost', 5092)
        self.device = DummyDAQ(
            bus_address=instAddr,
            num_slots=3,
            num_channels=20
        )
        self.device.open()
        self.device.start()
        self.daq = KeysightDAQ(
            bus_address=instAddr,
            num_slots=3,
            num_channels=20,
            delay=0
        )
        self.daq.open(read_term='\n', write_term='\n')

    def teardown_class(self):
        self.daq.close()
        self.device.close()
        self.device.join()
        self.device = None
        self.daq = None

    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    def test_get_id(self):
        id = self.daq.get_id()
        assert isinstance(id, str)

    def test_toggle_channel(self):
        ch = int('{:01d}{:02d}'.format(randint(1, 3), randint(1, 20)))
        was_open = self.daq.is_channel_open(ch)
        if was_open:
            self.daq.close_channel(ch)
        else:
            self.daq.open_channel(ch)
        now_open = self.daq.is_channel_open(ch)
        print('bbbbb')
        assert was_open ^ now_open

    def test_toggle_entire_slot(self):
        chs = [ch for ch in range(101, 121)]
        self.daq.open_all_channels(1)
        are_open = [self.daq.is_channel_open(ch) for ch in chs]
        self.daq.close_all_channels(1)
        are_closed = [self.daq.is_channel_closed(ch) for ch in chs]
        print('bbbbb')
        assert all(are_open) and all(are_closed)

    def test_toggle_channel_set(self):
        def randCh():
            return int('{:01d}{:02d}'.format(randint(1, 3), randint(1, 20)))
        chs = [randCh() for i in range(5)]
        self.daq.open_channels(chs)
        are_open = [self.daq.is_channel_open(ch) for ch in chs]
        self.daq.close_channels(chs)
        are_closed = [self.daq.is_channel_closed(ch) for ch in chs]
        assert all(are_open) and all(are_closed)

    def test_sensor_get(self):
        temp = self.daq.measure_temperature('FRTD', '85')
        rh = self.daq.measure_relative_humidity('FRTD', '85')
        assert temp >= 0 and temp <= 300
        assert rh >= 0 and rh <= 100


if __name__ == '__main__':
    dt = TestKeysightDAQ()
    dt.setup_class()
    dt.setup_method(dt.test_toggle_channel)
    dt.test_toggle_channel()
    dt.setup_method(dt.test_toggle_channel_set)
    dt.test_toggle_channel_set()
