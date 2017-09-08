
import time
import traceback
import sys
from pyvisainstrument.GPIBLink import GPIBLinkResource


class SwitchMainFrame(GPIBLinkResource):

    def __init__(self, busLinkAddress, numSlots, numChannels):
        """Initialize Agilint DAQ mainframe."""
        super(SwitchMainFrame, self).__init__(busAddress=busLinkAddress)
        self.busLinkAddress = busLinkAddress
        self.resourceLink = None
        self.numSlots = numSlots
        self.numChannels = numChannels
        self.delay = 150e-3

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

    def openAllChannels(self, slotIdx):
        for i in range(self.numChannels):
            chIdx = 100*slotIdx + (i+1);
            self.openChannel(chIdx);

    def closeAllChannels(self, slotIdx):
        for i in range(self.numChannels):
            chIdx = 100*slotIdx + (i+1);
            self.closeChannel(chIdx);

    def openChannels(self, channels):
        for ch in channels:
            self.openChannel(ch)

    def closeChannels(self, channels):
        for ch in channels:
            self.closeChannel(ch)

    def openChannel(self, channel):
        cmd = str.format("ROUT:OPEN (@{:03d});*OPC?", channel)
        self._querySCPI(cmd)

    def closeChannel(self, channel):
        cmd = str.format("ROUT:CLOS (@{:03d});*OPC?", channel)
        self._querySCPI(cmd)

    def _waitForCompletion(self, timeout=5):
        done = False
        waitTime = 0.0
        while not done:
            time.sleep(50E-3)
            doneStr = self._querySCPI("ROUT:DONE?")
            done = int(doneStr) if len(doneStr.strip()) else done
            waitTime += 50E-3
            if waitTime >= timeout:
                raise Exception("waitForCompletion:timeout")

    def _writeSCPI(self, scpiStr):
        print(str.format("DAQ.write({:s})", scpiStr))
        self.write(scpiStr)
        # self._waitForCompletion()

    def _querySCPI(self, scpiStr):
        attempts = 0
        while True:
            try:
                print(str.format("DAQ.query({:s})", scpiStr))
                rst = self.query(scpiStr)
                print(str.format("DAQ.query({:s}) -> {:s}", scpiStr, rst))
                return rst
            except Exception as err:
                attempts = attempts + 1
                if "Timeout" in str(err):
                    self.write("*CLS")
                    self.resource.flush(1)
                    self.write("*RST")
                if attempts > 4:
                    traceback.print_exc(file=sys.stdout)
                    raise err


if __name__ == '__main__':
    print("Starting")
    daq = SwitchMainFrame("TCPIP::127.0.0.1::5020::SOCKET", 3, 20)
    daq.open(baudRate=None, termChar='\n')
    daq.openAllChannels(1)
    daq.openChannels([101, 103, 105])
    daq.closeChannels([101, 103, 105])
    print("Finished")
