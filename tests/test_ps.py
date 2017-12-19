import pytest # NOQA
from multiprocessing import Process, Value
from ctypes import c_bool
import time
from pyvisainstrument import AgilentPowerSupply
from pyvisainstrument.testsuite import DummyPS

TCP_IP = '127.0.0.1'
TCP_PORT = 5090

def runDummyInstr(done):
    baseArgs = dict(tcpAddress=TCP_IP, tcpPort=TCP_PORT, termStr='\n', bufferSize=1024)
    instr = DummyPS(**baseArgs)
    instr.open()
    while not done.value:
        instr.run()

class TestAgilentPowerSupply(object):

    def setup_class(self):
        done = Value(c_bool, False)
        instAddr = "TCPIP::{:s}::{:d}::SOCKET".format(TCP_IP, TCP_PORT)
        self.dummyInst = Process(target=runDummyInstr, args=(done,))
        self.dummyInst.start()
        self.ps = AgilentPowerSupply(instAddr)
        self.done = done

    def teardown_class(self):
        # Set flag so instrument server knows we are done
        with self.done.get_lock():
            self.done.value = True
        # In order for inst server to handle closing must trigger new disconnect
        if self.ps:
            if not self.ps.isOpen:
                self.ps.open(readTerm='\n', writeTerm='\n')
            self.ps.close()
        if self.dummyInst:
            self.dummyInst.join(1)
            if self.dummyInst.is_alive():
                time.sleep(0.1)
                self.dummyInst.terminate()

    def setup_method(self, method):
        self.ps.open(readTerm='\n', writeTerm='\n')

    def teardown_method(self, method):
        self.ps.close()

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
