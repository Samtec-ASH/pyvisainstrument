"""NumatoRelay is a convenience class to control various Numato Lab Relay Modules."""
import time
from telnetlib import Telnet
import serial
from pyvisainstrument import AgilentDAQ


class NumatoRelay(AgilentDAQ):
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
        self.read_termination = None
        self.write_termination = None

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
            self.read_termination = readTerm or '\n\r'
            self.write_termination = writeTerm or '\n\r'
            self.resource = serial.Serial(self.busAddress, baudRate, timeout=1)
        # For Telnet (TCP) based modules
        elif 'TCP' in self.deviceType:
            self.read_termination = readTerm or '\r\n'
            self.write_termination = writeTerm or '\n\r'
            self.resource = Telnet(self.busAddress, timeout=1)
            self.resource.read_until(b"User Name: ")
            self.write(user)
            if password:
                self.resource.read_until(b"Password: ")
                self.write(password)
            self.resource.read_until(f"{self.read_termination}".encode('ascii'))
        else:
            raise ValueError(f'Unsupported device type: {self.deviceType}')
        self._clear_buffer()

    def close(self):
        """Clear and close instrument connection. """
        if self.resource:
            self.resource.close()

    def getID(self):
        ver = self.query('ver')
        return f'{self.name} {ver}'

    def getChannelState(self, channel, numAttempts=3):
        """Get state of {channel} (int). Return 1 if closed else 0 if open"""
        if int(channel) >= self.numChannels or int(channel) < 0:
            raise Exception(f'Channel must be in range [0,{self.numChannels-1}]')
        err = None
        for _ in range(numAttempts):
            try:
                msg = self.query(f"relay read {channel}")
                self._clear_buffer()
                idx = 1 if 'on' in msg else 0 if 'off' in msg else -1
                if idx == 0 or idx == 1: return idx
            except Exception as e:
                err = e
        raise Exception(f'Failed to get channel state {msg}. {err}')

    def isChannelClosed(self, channel):
        """Check if {channel} (int) is closed. """
        return self.getChannelState(channel) == 1

    def isChannelOpen(self, channel):
        """Check if {channel} (int) is open. """
        return self.getChannelState(channel) == 0

    def openAllChannels(self, slotIdx=1, delay=0):
        """Open all channels for {slotIdx} (int) w/ {delay} (Optional[int]). """
        for ch in range(self.numChannels):
            self.openChannel(ch)

    def closeAllChannels(self, slotIdx=1, delay=0):
        """Close all channels for {slotIdx} (int) w/ {delay} (Optional[int]). """
        for ch in range(self.numChannels):
            self.closeChannel(ch, delay)

    def openChannels(self, channels, delay=0):
        """Open specified {channels} (List[int]) w/ {delay} (Optional[int]). """
        for ch in channels:
            self.openChannel(ch, delay)

    def closeChannels(self, channels, delay=0):
        """Close specified {channels} (List[int]) w/ {delay} (Optional[int]). """
        for ch in channels:
            self.closeChannel(ch, delay)

    def setChannel(self, channel, on, delay, numAttempts=3):
        """Set specified {channel} (int) on or off w/ {delay} (Optional[int]) and {numAttempts} (int)."""
        err = None
        for _ in range(numAttempts):
            try:
                self.write(f"relay {'on' if on else 'off'} {channel}")
                time.sleep(delay)
                if self.getChannelState(channel) == on:
                    return
                self._clear_buffer()
            except Exception as e:
                err = e
        raise Exception(f"Failed to set channel {channel} {'on' if on else 'off'}. {err}")

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

    def read(self):
        """Read from resource """
        if 'TCP' in self.deviceType:
            return self.resource.read_until(f'{self.read_termination}>'.encode('ascii'), timeout=1).decode()
        return self.resource.read_until(f'{self.read_termination}>'.encode('ascii')).decode()

    def write(self, cmd, reset_input=True):
        """Write cmd to resource."""
        self.resource.write(f'{cmd}{self.write_termination}'.encode('ascii'))
        if reset_input:
            time.sleep(0.1)
            self._clear_buffer()

    def query(self, cmd):
        """Perform write followed by read."""
        self.write(cmd, reset_input=False)
        msg = self.read()
        msg = msg.replace(f'{cmd}\n{self.read_termination}', '')  # Remove sent cmd
        msg = msg.replace(f'{self.read_termination}>', '') # Remove result term
        return msg

    def _clear_buffer(self):
        """Try to empty IO buffers. (useful when in unknown state)."""
        if 'USB' in self.deviceType:
            self.resource.reset_input_buffer()
            self.resource.reset_output_buffer()
