"""AgilentDAQ is a convenience class to control various Agilent Switch DAQs."""
from __future__ import print_function
import time
from pyvisainstrument.VisaResource import VisaResource

# pylint: disable=too-many-public-methods
class AgilentDAQ(VisaResource):
    """AgilentDAQ is a convenience class to control various Agilent Switch DAQs."""
    # pylint: disable=too-many-arguments
    def __init__(self, numSlots, numChannels, *args, **kwargs):
        super(AgilentDAQ, self).__init__(name='DAQ', *args, **kwargs)
        self.numSlots = numSlots
        self.numChannels = numChannels

    def isChannelClosed(self, channel):
        """Get if channel is closed.
        Args:
            channel (int): Actuator with format SCC
        Returns:
            bool: True if channel is closed
        """
        return self.query('ROUT:CLOS? (@{:03d})'.format(channel)) == '1'

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
        self.write('ROUT:OPEN (@{:03d})'.format(channel))
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
        self.write('ROUT:CLOS (@{:03d})'.format(channel))
        time.sleep(delay)

    def waitForCompletion(self, timeout=2):
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
            doneStr = self.resource.query('ROUT:DONE?', delay=15E-3)
            if isinstance(doneStr, str) and doneStr.strip().isnumeric():
                done = int(doneStr.strip())
            waitTime += 15E-3
            if waitTime >= timeout:
                raise Exception("waitForCompletion:timeout")


if __name__ == '__main__':
    print('Started')
    daq = AgilentDAQ(
        busAddress='TCPIP::127.0.0.1::5020::SOCKET',
        numSlots=3,
        numChannels=20
    )
    daq.open(baudRate=None, readTerm='\n', writeTerm='\n')
    daq.openAllChannels(1)
    daq.openChannels([101, 103, 105])
    daq.closeChannels([101, 103, 105])
    print("Finished")
