
"""SwitchMainFrame is a convience class to control various Agilent Switch DAQs.
"""

from __future__ import print_function
import time
from pyvisainstrument.GPIBLink import GPIBLinkResource

# pylint: disable=too-many-public-methods
class SwitchMainFrame(GPIBLinkResource):
    """SwitchMainFrame is a convience class to control various Agilent Switch DAQs.
    Attributes:
        None
    """
    # pylint: disable=too-many-arguments
    def __init__(self, busLinkAddress, numSlots, numChannels, delay=15e-3, verbose=False):
        super(SwitchMainFrame, self).__init__(busAddress=busLinkAddress)
        self.verbose = verbose
        self.busLinkAddress = busLinkAddress
        self.resourceLink = None
        self.numSlots = numSlots
        self.numChannels = numChannels
        self.delay = delay

    # pylint: disable=arguments-differ,useless-super-delegation
    def open(self, *args, **kwargs):
        """Open instrument connection.
        Args:
            None
        Returns:
            None
        """
        super(SwitchMainFrame, self).open(*args, **kwargs)

    # pylint: disable=arguments-differ,useless-super-delegation
    def close(self):
        """Close instrument connection.
        Args:
            None
        Returns:
            None
        """
        super(SwitchMainFrame, self).close()

    def getID(self):
        """Get identifier.
        Args:
            None
        Returns:
            str: ID
        """
        return str(self._querySCPI("*IDN?"))

    def isChannelClosed(self, channel):
        """Get if channel is closed.
        Args:
            channel (int): Actuator with format SCC
        Returns:
            bool: True if channel is closed
        """
        cmd = str.format("ROUT:CLOS? (@{:03d})", channel)
        rst = self._querySCPI(cmd)
        return rst == '1'

    def isChannelOpen(self, channel):
        """Get if channel is open.
        Args:
            channel (int): Actuator with format SCC
        Returns:
            bool: True if channel is open
        """
        return not self.isChannelClosed(channel)

    def openAllChannels(self, slotIdx, delay=0):
        """Open all channels of a slot.
        Args:
            slotIdx (int): Slot index (1-based)
        Returns:
            None
        """
        for i in range(self.numChannels):
            chIdx = 100*slotIdx + (i+1)
            self.openChannel(chIdx)
            time.sleep(delay)

    def closeAllChannels(self, slotIdx, delay=0):
        """Close all channels of a slot.
        Args:
            slotIdx (int): Slot index (1-based)
            delay (int, optional):
                Delay between each channel operation.
                Default is 0 - no delay
        Returns:
            None
        """
        for i in range(self.numChannels):
            chIdx = 100*slotIdx + (i+1)
            self.closeChannel(chIdx, delay)

    def openChannels(self, channels, delay=0):
        """Open specified channels.
        Args:
            channels ([int]):
                Channel indices with format SCC
            delay (int, optional):
                Delay between each channel operation.
                Default is 0 - no delay
        Returns:
            None
        """
        for ch in channels:
            self.openChannel(ch, delay)

    def closeChannels(self, channels, delay=0):
        """Close specified channels.
        Args:
            channels ([int]):
                Channel indices with format SCC
            delay (int, optional):
                Delay between each channel operation.
                Default is 0 - no delay
        Returns:
            None
        """
        for ch in channels:
            self.closeChannel(ch, delay)

    def openChannel(self, channel, delay=0):
        """Open specified channel.
        Args:
            channel (int):
                Channel index with format SCC
            delay (int, optional):
                Delay after channel operation.
                Default is 0 - no delay
        Returns:
            None
        """
        cmd = str.format("ROUT:OPEN (@{:03d})", channel)
        self._writeSCPI(cmd)
        time.sleep(delay)

    def closeChannel(self, channel, delay=0):
        """Close specified channel.
        Args:
            channel (int):
                Channel index with format SCC
            delay (int, optional):
                Delay after channel operation.
                Default is 0 - no delay
        Returns:
            None
        """
        cmd = str.format("ROUT:CLOS (@{:03d})", channel)
        self._writeSCPI(cmd)
        time.sleep(delay)

    def _waitForCompletion(self, timeout=2):
        """Wait for physical operation to complete.
        Args:
            timeout (float):
                Max time to wait for completion in secs.
        Returns:
            Exception if timeout reached
        """
        done = False
        waitTime = 0.0
        while not done:
            time.sleep(15E-3)
            doneStr = self._querySCPI("ROUT:DONE?")
            if isinstance(doneStr, str) and doneStr.strip().isnumeric():
                done = int(doneStr.strip())
            waitTime += 15E-3
            if waitTime >= timeout:
                raise Exception("waitForCompletion:timeout")

    def _writeSCPI(self, scpiStr):
        """Perform raw SCPI write
        Args:
            scpiStr (str): SCPI command
        Returns:
            None
        """
        if self.verbose:
            print(str.format("DAQ.write({:s})", scpiStr))
        self.write(scpiStr)
        self._waitForCompletion()

    def _querySCPI(self, scpiStr):
        """Perform raw SCPI query
        Args:
            scpiStr (str): SCPI query
        Returns:
            str: Query result
        """
        rst = self.query(scpiStr)
        if self.verbose:
            print(str.format("DAQ.query({:s}) -> {:s}", scpiStr, rst))
        return rst


if __name__ == '__main__':
    print("Starting")
    daq = SwitchMainFrame("TCPIP::127.0.0.1::5020::SOCKET", 3, 20)
    daq.open(baudRate=None, termChar='\n')
    daq.openAllChannels(1)
    daq.openChannels([101, 103, 105])
    daq.closeChannels([101, 103, 105])
    print("Finished")
