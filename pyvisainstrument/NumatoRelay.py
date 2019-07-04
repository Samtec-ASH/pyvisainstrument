"""NumatoRelay is a convenience class to control various Numato Lab Relay Modules."""
import time
from telnetlib import Telnet
import serial


class NumatoRelay:
    """NumatoRelay is a convenience class to control various Numato Lab Relay Modules."""
    # pylint: disable=too-many-arguments
    def __init__(self, name, busAddress, numSlots, numChannels, verbose=False, delay=20e-3):
        self.name = name
        # busAddress is formated like GPIB device DEVICE_TYPE::ADDRESS
        # such as TCP::127.0.0.0 or USB::/dev/ttyACMO
        addressParts = busAddress.split('::') if '::' in busAddress else ['USB', busAddress]
        self.deviceType = addressParts[0].upper().strip()
        self.busAddress = addressParts[1]
        self.resource = None
        self.delay = delay
        self.numSlots = 1 or numSlots # Only have 1 slot
        self.numChannels = numChannels

    def open(self, readTerm=None, writeTerm=None, baudRate=19200, user='admin', password='admin'):
        """Open instrument connection.
        Args:
            baudRate (int, optional): Baud rate in hertz
            readTerm (str, optional): Read termination chars
            writeTerm (str, optional): Write termination chars
            user (str, optional): username for TCP comm.
            password (str, optional): password for TCP comm.
        Returns:
            None
        """
        # USB device
        if 'USB' in self.deviceType:
            self.resource = serial.Serial(self.busAddress, baudRate, timeout=1)
            self.resource.reset_input_buffer()
            self.resource.reset_output_buffer()
        # For Telnet (TCP) based modules
        elif 'TCP' in self.deviceType:
            self.resource = Telnet(self.busAddress, timeout=1)
            self.resource.read_until(b"User Name: ")
            self.resource.write(f"{user}\n\r".encode('ascii'))
            if password:
                self.resource.read_until(b"Password: ")
                self.resource.write(f'{password}\n\r'.encode('ascii'))
            self.resource.read_until(b"\r\n>")
        else:
            raise ValueError(f'Unsupported device type: {self.deviceType}')

    def close(self):
        """Clear and close instrument connection.
        Args:
            None
        Returns:
            None
        """
        if self.resource:
            self.resource.close()

    def getChannelState(self, channel):
        """Get channel state.
        Args:
            channel (int): Channel index
        Returns:
            int: 1 if closed, 0 if open
        """
        if int(channel) >= self.numChannels or int(channel) < 0:
            raise Exception(f'Channel must be in range [0,{self.numChannels-1}]')
        idx = -1
        if 'USB' in self.deviceType:
            self.resource.write(f"relay read {channel}\n\r".encode('ascii'))
            msg = self.resource.read_until(b'\n\r>')
            idx = 1 if b'on' in msg else 0 if b'off' in msg else -1
        elif 'TCP' in self.deviceType:
            self.resource.write(f"relay read {channel}\r\n".encode('ascii'))
            msg = self.resource.read_until(b'\r\n>', timeout=1)
            idx = 1 if b'on' in msg else 0 if b'off' in msg else -1
        if idx <= -1:
            raise Exception(f'Failed to get channel state {msg}.')
        return idx

    def isChannelClosed(self, channel):
        """Check if channel is closed.
        Args:
            channel (int): Channel index
        Returns:
            bool: True if channel is open
        """
        return self.getChannelState(channel) == 1

    def isChannelOpen(self, channel):
        """Check if channel is open.
        Args:
            channel (int): Channel index
        Returns:
            bool: True if channel is open
        """
        return self.getChannelState(channel) == 0

    def openAllChannels(self, slotIdx=1, delay=0):
        """Open all channels of a slot.
        Args:
            slotIdx (int): Slot index (1-based)
            delay (int, optional): Delay after operation (default 0).
        """
        for ch in range(self.numChannels):
            self.openChannel(ch)
            time.sleep(delay)

    def closeAllChannels(self, slotIdx=1, delay=0):
        """Close all channels of a slot.
        Args:
            slotIdx (int): Slot index (1-based)
            delay (int, optional): Delay after operation (default 0).
        """
        for ch in range(self.numChannels):
            self.closeChannel(ch, delay)

    def openChannels(self, channels, delay=0):
        """Open specified channels.
        Args:
            channels ([int]): Channel indices
            delay (int, optional): Delay after operation (default 0).
        """
        for ch in channels:
            self.openChannel(ch, delay)

    def closeChannels(self, channels, delay=0):
        """Close specified channels.
        Args:
            channels ([int]): Channel indices
            delay (int, optional): Delay after operation (default 0).
        """
        for ch in channels:
            self.closeChannel(ch, delay)

    def setChannel(self, channel, on, delay):
        """Set specified channel on or off.
        Args:
            channel (int): Channel index
            delay (int, optional): Delay after operation (default 0).
        """
        if 'USB' in self.deviceType:
            self.resource.write(f"relay {'on' if on else 'off'} {channel}\n\r".encode('ascii'))
            self.resource.reset_input_buffer()
        elif 'TCP' in self.deviceType:
            self.resource.write(f"relay {'on' if on else 'off'} {channel}\r\n".encode('ascii'))
        time.sleep(delay)

    def openChannel(self, channel, delay=0):
        """Open specified channel.
        Args:
            channel (int): Channel index
            delay (int, optional): Delay after operation (default 0).
        """
        self.setChannel(channel, on=False, delay=delay)

    def closeChannel(self, channel, delay=0):
        """Close specified channel.
        Args:
            channel (int): Channel index
            delay (int, optional): Delay after operation (default 0).
        """
        self.setChannel(channel, on=True, delay=delay)
