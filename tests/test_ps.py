import pytest # NOQA
import threading
import time
from pyvisainstrument import AgilentPowerSupply
from pyvisainstrument.testsuite import DummyPS

class TestAgilentPowerSupply(object):

    def setup_method(self, test_method):
        self.dummyThread = threading.Thread(target=self.runDummyPS, name="PS")
        self.dummyThread.start()
        time.sleep(1)
        self.ps = AgilentPowerSupply("TCPIP::127.0.0.1::5099::SOCKET")
        self.ps.open(readTerm='\n', writeTerm='\n')

    def runDummyPS(self):
        TCP_IP = '127.0.0.1'
        TCP_PORT = 5099
        baseArgs = dict(tcpAddress=TCP_IP, tcpPort=TCP_PORT, termStr='\n', bufferSize=1024)
        instr = DummyPS(**baseArgs)
        instr.open()
        instr.run()

    def teardown_method(self, test_method):
        self.ps.close()

    def test_getID(self):
        id = self.ps.getID()
        assert isinstance(id, str)

    def test_setVoltage(self):
        self.ps.setChannel(1)
        self.ps.enable()
        self.ps.setCurrentLimit(2)
        self.ps.setVoltageSetPoint(5.0)
        print(self.ps.getCurrentLimit())
        print(self.ps.getVoltageSetPoint())
        self.ps.disable()
        assert True
