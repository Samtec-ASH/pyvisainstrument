import pytest # NOQA
from multiprocessing import Process, Value
import threading
from ctypes import c_bool
import time
from pyvisainstrument import AgilentVNA
from pyvisainstrument.testsuite import DummyVNA

TCP_IP = '127.0.0.1'
TCP_PORT = 5050

def runDummyInstr(done):
    baseArgs = dict(tcpAddress=TCP_IP, tcpPort=TCP_PORT, termStr='\n', bufferSize=1024)
    instr = DummyVNA(**baseArgs)
    instr.open()
    while not done.value:
        instr.run()

class TestAgilentVNA(object):

    def setup_class(self):
        done = Value(c_bool, False)
        instAddr = "TCPIP::{:s}::{:d}::SOCKET".format(TCP_IP, TCP_PORT)
        self.vnaThread = threading.Thread(target=runDummyInstr, name="VNA")
        self.vnaThread.start()
        self.dummyInst = Process(target=runDummyInstr, args=(done,))
        self.dummyInst.start()
        self.vna = AgilentVNA(instAddr)
        self.done = done

    def teardown_class(self):
        # self.vna.close()
        # self.vnaThread.join()
        # Set flag so instrument server knows we are done
        with self.done.get_lock():
            self.done.value = True
        # In order for inst server to handle closing must trigger new disconnect
        if self.vna:
            if not self.vna.isOpen:
                self.vna.open(readTerm='\n', writeTerm='\n')
            self.vna.close()
        if self.dummyInst:
            self.dummyInst.join(1)
            if self.dummyInst.is_alive():
                time.sleep(0.5)
                self.dummyInst.terminate()

    def setup_method(self, method):
        self.vna.open(readTerm='\n', writeTerm='\n')

    def teardown_method(self, method):
        self.vna.close()

    def test_getID(self):

        id = self.vna.getID()

        assert isinstance(id, str)

    def test_setSweep(self):
        self.vna.setupSweep(
            1E7,
            2E10,
            2000,
            sweepType="LINEAR",
            channel=1
        )
        startFreq = self.vna.getStartFreq()
        stopFreq = self.vna.getStopFreq()
        sweepPoints = self.vna.getNumberSweepPoints()
        sweepType = self.vna.getSweepType()
        assert startFreq == 1E7
        assert stopFreq == 2E10
        assert sweepPoints == 2000
        assert sweepType == "LINEAR"

    def test_performEcal(self):
        self.vna.setupSweep(
            1E7,
            2E10,
            2000,
            sweepType="LINEAR",
            channel=1
        )
        self.vna.setupECalibration(
            portConnectors=['2.92 mm female' for i in range(4)],
            portKits=['N4692-60003 ECal 13226' for i in range(4)],
            portThruPairs=[1, 2, 1, 3, 1, 4],
            autoOrient=True
        )
        numSteps = self.vna.getNumberECalSteps()
        print(numSteps)
        steps = [self.vna.getECalStepInfo(step) for step in range(numSteps)]
        print(steps)
        for i, step in enumerate(steps):
            self.vna.performECalStep(i, save=True, delay=0)
        assert True
