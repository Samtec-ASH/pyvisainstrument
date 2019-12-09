import pytest  # NOQA
from ctypes import c_bool
import time
from pyvisainstrument import KeysightPSU
from pyvisainstrument.testsuite import DummyPS


class TestKeysightPSU:

    def setup_class(self):
        instAddr = "TCPIP::{:s}::{:d}::SOCKET".format('localhost', 5020)
        self.device = DummyPS(bus_address=instAddr)
        self.device.open(read_term='\n', write_term='\n')
        self.device.start()
        self.ps = KeysightPSU(bus_address=instAddr, delay=0)
        self.ps.open(read_term='\n', write_term='\n')

    def teardown_class(self):
        self.ps.close()
        self.device.close()
        self.device.join()
        self.device = None
        self.ps = None

    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    def test_get_id(self):
        id = self.ps.get_id()
        assert isinstance(id, str)

    def test_set_voltage(self):
        self.ps.set_channel(1)
        self.ps.enable()
        self.ps.set_voltage_set_point(5.0)
        volt = self.ps.get_voltage_set_point()
        self.ps.disable()
        assert volt == 5.0
