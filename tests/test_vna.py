import pytest # NOQA
from multiprocessing import Process, Value
import threading
from ctypes import c_bool
import time
from pyvisainstrument import AgilentVNA
from pyvisainstrument.testsuite import DummyVNA

class TestAgilentVNA:

    def setup_class(self):
        instAddr = 'TCPIP::{0}::{1}::SOCKET'.format('localhost', 5051)
        self.device = DummyVNA(numPorts=4, busAddress=instAddr)
        self.device.open(readTerm='\n', writeTerm='\n')
        self.device.start()
        self.vna = AgilentVNA(numPorts=4, busAddress=instAddr, delay=2e-2)
        self.vna.open(readTerm='\n', writeTerm='\n')

    def teardown_class(self):
        self.vna.close()
        self.vna = None

        self.device.close()
        self.device.join()

    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

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
        portPairs = [[0,2],[0,2]]
        traceNames = self.vna.setupSESTraces(portPairs=portPairs)
        sData = self.vna.captureSESTrace(dtype=complex, portPairs=portPairs)
        print(sData)
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
        steps = [self.vna.getECalStepInfo(step) for step in range(numSteps)]
        for i, step in enumerate(steps):
            self.vna.performECalStep(i, save=True, delay=0)
        assert True
