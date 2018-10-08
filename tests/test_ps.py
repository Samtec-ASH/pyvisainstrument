import pytest # NOQA
from ctypes import c_bool
import time
from pyvisainstrument import AgilentPowerSupply
from pyvisainstrument.testsuite import DummyPS

class TestAgilentPowerSupply:

    def setup_class(self):
        instAddr = "TCPIP::{:s}::{:d}::SOCKET".format('localhost', 5020)
        self.device = DummyPS(busAddress=instAddr)
        self.device.open(readTerm='\n', writeTerm='\n')
        self.device.start()
        self.ps = AgilentPowerSupply(busAddress=instAddr, delay=0)
        self.ps.open(readTerm='\n', writeTerm='\n')

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

    def test_getID(self):
        id = self.ps.getID()
        assert isinstance(id, str)

    def test_setVoltage(self):
        self.ps.setChannel(1)
        self.ps.enable()
        self.ps.setVoltageSetPoint(5.0)
        volt = self.ps.getVoltageSetPoint()
        self.ps.disable()
        assert volt == 5.0
