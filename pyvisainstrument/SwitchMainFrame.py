
import time
import traceback
import sys
from pyvisainstrument.GPIBLink import GPIBLinkResource


class SwitchMainFrame(GPIBLinkResource):

    def __init__(self, busLinkAddress, numSlots, numChannels, delay=15e-3):
        """Initialize Agilint DAQ mainframe."""
        super(SwitchMainFrame, self).__init__(busAddress=busLinkAddress)
        self.busLinkAddress = busLinkAddress
        self.resourceLink = None
        self.numSlots = numSlots
        self.numChannels = numChannels
        self.delay = delay

    def open(self, baudRate=115200, readTerm=None, writeTerm=None):
        super(SwitchMainFrame, self).open()
        if baudRate:
            self.resource.baud_rate = baudRate
        if readTerm:
            self.resource.read_termination = readTerm
        if writeTerm:
            self.resource.write_termination = writeTerm

    def close(self):
        super(SwitchMainFrame, self).close()

    def getID(self):
        return str(self._querySCPI("*IDN?"))

    def isChannelClosed(self, channel):
        cmd = str.format("ROUT:CLOS? (@{:03d})", channel)
        rst = self._querySCPI(cmd)
        return rst == '1'

    def isChannelOpen(self, channel):
        return not self.isChannelClosed(channel)

    def openAllChannels(self, slotIdx, delay=0):
        for i in range(self.numChannels):
            chIdx = 100*slotIdx + (i+1)
            self.openChannel(chIdx)
            time.sleep(delay)

    def closeAllChannels(self, slotIdx, delay=0):
        for i in range(self.numChannels):
            chIdx = 100*slotIdx + (i+1)
            self.closeChannel(chIdx, delay)

    def openChannels(self, channels, delay=0):
        for ch in channels:
            self.openChannel(ch, delay)

    def closeChannels(self, channels, delay=0):
        for ch in channels:
            self.closeChannel(ch, delay)

    def openChannel(self, channel, delay=0):
        cmd = str.format("ROUT:OPEN (@{:03d})", channel)
        self._writeSCPI(cmd)
        time.sleep(delay)

    def closeChannel(self, channel, delay=0):
        cmd = str.format("ROUT:CLOS (@{:03d})", channel)
        self._writeSCPI(cmd)
        time.sleep(delay)

    def _waitForCompletion(self, timeout=2):
        done = False
        waitTime = 0.0
        while not done:
            time.sleep(15E-3)
            doneStr = self._querySCPI("ROUT:DONE?")
            done = int(doneStr) if len(doneStr.strip()) else done
            waitTime += 15E-3
            if waitTime >= timeout:
                raise Exception("waitForCompletion:timeout")

    def _writeSCPI(self, scpiStr):
        print(str.format("DAQ.write({:s})", scpiStr))
        self.write(scpiStr)
        self._waitForCompletion()

    def _querySCPI(self, scpiStr):
        rst = self.query(scpiStr)
        return rst

if __name__ == '__main__':
    print("Starting")
    daq = SwitchMainFrame("TCPIP::127.0.0.1::5020::SOCKET", 3, 20)
    daq.open(baudRate=None, termChar='\n')
    daq.openAllChannels(1)
    daq.openChannels([101, 103, 105])
    daq.closeChannels([101, 103, 105])
    print("Finished")
