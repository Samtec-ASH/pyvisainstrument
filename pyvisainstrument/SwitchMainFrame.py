
import time
from pyvisainstrument.GPIBLink import GPIBLinkResource


class SwitchMainFrame(GPIBLinkResource):

    def __init__(self, busLinkAddress, numSlots, numChannels):
        """Initialize Agilint DAQ mainframe."""
        super(SwitchMainFrame, self).__init__(busAddress=busLinkAddress)
        self.busLinkAddress = busLinkAddress
        self.resourceLink = None
        self.numSlots = numSlots
        self.numChannels = numChannels

    def open(self, baudRate=115200, termChar=None):
        super(SwitchMainFrame, self).open()
        if baudRate is not None:
            self.resource.baud_rate = baudRate
        if termChar is not None:
            self.resource.read_termination = termChar

    def close(self):
        super(SwitchMainFrame, self).close()

    def getID(self):
        return str(self._querySCPI("*IDN?"))

    def openAllChannels(self, slotIdx):
        cmd = str.format("ROUT:OPEN (@{:d}{:02d}:{:d}{:02d})",
                         slotIdx,
                         1,
                         slotIdx,
                         self.numChannels)
        self._writeSCPI(cmd)

    def openChannels(self, channels):
        chStr = ','.join([str.format("{:03d}", int(ch)) for ch in channels])
        cmd = str.format("ROUT:OPEN (@{:s})", chStr)
        self._writeSCPI(cmd)

    def closeChannels(self, channels):
        chStr = ','.join([str.format("{:03d}", int(ch)) for ch in channels])
        cmd = str.format("ROUT:CLOS (@{:s})", chStr)
        self._writeSCPI(cmd)

    def _waitForCompletion(self, timeout=5):
        done = False
        waitTime = 0.0
        while not done:
            time.sleep(15E-3)
            done = int(self._querySCPI("ROUT:DONE?"))
            waitTime += 15E-3
            if waitTime >= timeout:
                raise Exception("waitForCompletion:timeout")

    def _writeSCPI(self, scpiStr):
        self.write(scpiStr)
        self._waitForCompletion()

    def _querySCPI(self, scpiStr):
        return self.query(scpiStr)


if __name__ == '__main__':
    print("Starting")
    daq = SwitchMainFrame("TCPIP::127.0.0.1::5020::SOCKET", 3, 20)
    daq.open(baudRate=None, termChar='\n')
    daq.openAllChannels(1)
    daq.openChannels([101, 103, 105])
    daq.closeChannels([101, 103, 105])
    print("Finished")
