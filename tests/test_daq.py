import pytest # NOQA
from multiprocessing import Process, Value
from ctypes import c_bool
import time
from random import randint
from pyvisainstrument import SwitchMainFrame
from pyvisainstrument.testsuite import DummyDAQ

def runDummyDAQInstr(done):
    baseArgs = dict(
        numPorts=3,
        numChannels=20,
        tcpAddress='localhost',
        tcpPort=5092,
        termStr='\n',
        bufferSize=1024
    )
    instr = DummyDAQ(**baseArgs)
    instr.open()
    while not done.value:
        instr.run()

class TestSwitchMainFrame(object):

    def setup_class(self):
        done = Value(c_bool, False)
        instAddr = "TCPIP::{:s}::{:d}::SOCKET".format('localhost', 5092)
        self.dummyInst = Process(target=runDummyDAQInstr, args=(done,))
        self.dummyInst.start()
        self.daq = SwitchMainFrame(instAddr, 3, 20, delay=0)
        self.done = done

    def teardown_class(self):
        # Set flag so instrument server knows we are done
        with self.done.get_lock():
            self.done.value = False
        # In order for inst server to handle closing must trigger new disconnect
        if self.daq:
            if not self.daq.isOpen:
                self.daq.open(readTerm='\n', writeTerm='\n')
            self.daq.close()
        if self.dummyInst:
            self.dummyInst.join(1)
            if self.dummyInst.is_alive():
                time.sleep(0.1)
                self.dummyInst.terminate()

    def setup_method(self, method):
        self.daq.open(readTerm='\n', writeTerm='\n')

    def teardown_method(self, method):
        self.daq.close()
        time.sleep(0.5)

    def test_getID(self):
        id = self.daq.getID()
        assert isinstance(id, str)

    def test_toggleChannel(self):
        ch = int('{:01d}{:02d}'.format(randint(1, 3), randint(1, 20)))
        wasOpen = self.daq.isChannelOpen(ch)
        if wasOpen:
            self.daq.closeChannel(ch)
        else:
            self.daq.closeChannel(ch)
        nowOpen = self.daq.isChannelOpen(ch)
        assert wasOpen ^ nowOpen

    def test_toggleEntireSlot(self):
        chs = [ch for ch in range(101, 121)]
        self.daq.openAllChannels(1)
        areOpen = [self.daq.isChannelOpen(ch) for ch in chs]
        self.daq.closeAllChannels(1)
        areClosed = [self.daq.isChannelClosed(ch) for ch in chs]
        assert all(areOpen) and all(areClosed)

    def test_toggleChannelSet(self):
        def randCh():
            return int('{:01d}{:02d}'.format(randint(1, 3), randint(1, 20)))
        chs = [randCh() for i in range(5)]
        self.daq.openChannels(chs)
        areOpen = [self.daq.isChannelOpen(ch) for ch in chs]
        self.daq.closeChannels(chs)
        areClosed = [self.daq.isChannelClosed(ch) for ch in chs]
        assert all(areOpen) and all(areClosed)
