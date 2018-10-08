import pytest # NOQA
from ctypes import c_bool
import time
from random import randint
from pyvisainstrument import AgilentDAQ
from pyvisainstrument.testsuite import DummyDAQ


class TestAgilentDAQ:

    def setup_class(self):
        instAddr = "TCPIP::{:s}::{:d}::SOCKET".format('localhost', 5092)
        self.device = DummyDAQ(
            busAddress=instAddr,
            numSlots=3,
            numChannels=20
        )
        self.device.open()
        self.device.start()
        self.daq = AgilentDAQ(
            busAddress=instAddr,
            numSlots=3,
            numChannels=20,
            delay=0
        )
        self.daq.open(readTerm='\n', writeTerm='\n')

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
