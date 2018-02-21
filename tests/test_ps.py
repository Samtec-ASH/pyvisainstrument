import pytest # NOQA
from multiprocessing import Process, Value
from ctypes import c_bool
import time
from pyvisainstrument import AgilentPowerSupply
from pyvisainstrument.testsuite import DummyPS


def runDummyPSInstr(done):
    baseArgs = dict(tcpAddress='localhost', tcpPort=5020, termStr='\n', bufferSize=1024)
    instr = DummyPS(**baseArgs)
    instr.open()
    while not done.value:
        instr.run()

class TestAgilentPowerSupply(object):

    def setup_class(self):
        done = Value(c_bool, False)
        instAddr = "TCPIP::{:s}::{:d}::SOCKET".format('localhost', 5020)
        self.dummyInst = Process(target=runDummyPSInstr, args=(done,))
        self.dummyInst.start()
        self.ps = AgilentPowerSupply(instAddr)
        self.done = done

    def teardown_class(self):
        # Set flag so instrument server knows we are done
        with self.done.get_lock():
            self.done.value = False
        # In order for inst server to handle closing must trigger new disconnect
        if self.ps:
            if not self.ps.isOpen:
                self.ps.open(readTerm='\n', writeTerm='\n')
            self.ps.close()
        if self.dummyInst:
            self.dummyInst.join(1)
            if self.dummyInst.is_alive():
                time.sleep(0.5)
                self.dummyInst.terminate()

    def setup_method(self, method):
        self.ps.open(readTerm='\n', writeTerm='\n')

    def teardown_method(self, method):
        self.ps.close()
        time.sleep(0.5)

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
