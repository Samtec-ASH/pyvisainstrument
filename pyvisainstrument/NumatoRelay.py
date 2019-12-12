"""NumatoRelay is a convenience class to control various Numato Lab Relay Modules."""
import time
from typing import List, Optional, Union
from telnetlib import Telnet
from serial import Serial
from pyvisainstrument import KeysightDAQ


class NumatoRelay(KeysightDAQ):
    """NumatoRelay is a convenience class to control various Numato Lab Relay Modules."""

    def __init__(self, *args, **kwargs):
        super(NumatoRelay, self).__init__(*args, **kwargs)
        # bus_address is formated like GPIB device DEVICE_TYPE::ADDRESS
        # such as TCP::127.0.0.0 or USB::/dev/ttyACMO
        bus_address = kwargs.get('bus_address')
        address_parts = bus_address.split('::') if '::' in bus_address else ['USB', bus_address]
        self.device_type = address_parts[0].upper().strip()
        self.bus_address = address_parts[1]
        self.resource: Optional[Union[Serial, Telnet]] = None
        self.read_termination = None
        self.write_termination = None

    # pylint: disable=arguments-differ
    def open(
            self, read_term: Optional[str] = None, write_term: Optional[str] = None, baud_rate: Optional[int] = 19200,
            user: str = 'admin', password: str = 'admin'):
        """ Open instrument connection.
        Args:
            baud_rate (int, optional): Baud rate in hertz
            read_term (str, optional): Read termination chars
            write_term (str, optional): Write termination chars
            user (str, optional): username for TCP comm.
            password (str, optional): password for TCP comm.
        Returns:
            None
        """
        # USB device
        if 'USB' in self.device_type:
            self.read_termination = read_term or '\n\r'
            self.write_termination = write_term or '\n\r'
            self.resource = Serial(self.bus_address, baud_rate, timeout=1)
        # For Telnet (TCP) based modules
        elif 'TCP' in self.device_type:
            self.read_termination = read_term or '\r\n'
            self.write_termination = write_term or '\n\r'
            self.resource = Telnet(self.bus_address, timeout=1)
            self.resource.read_until(b"User Name: ")
            self.write(user)
            if password:
                self.resource.read_until(b"Password: ")
                self.write(password)
            self.resource.read_until(f"{self.read_termination}".encode('ascii'))
        else:
            raise ValueError(f'Unsupported device type: {self.device_type}')
        self._clear_buffer()

    def close(self):
        """ Clear and close instrument connection. """
        if self.resource:
            self.resource.close()

    def get_id(self):
        """ Get ID of device.
        Returns:
            str: ID
        """
        ver = self.query('ver')
        return f'{self.name} {ver}'

    def get_channel_state(self, channel: Union[int, str], num_attempts: int = 3):
        """ Get state of {channel} (int). Return 1 if closed else 0 if open"""
        if int(channel) >= self.num_channels or int(channel) < 0:
            raise Exception(f'Channel must be in range [0,{self.num_channels-1}]')
        err = None
        msg = ''
        for _ in range(num_attempts):
            try:
                msg = self.query(f'relay read {channel}')
                self._clear_buffer()
                idx = 1 if 'on' in msg else 0 if 'off' in msg else -1
                if idx in (0, 1):
                    return idx
            except Exception as e:
                err = e
        raise Exception(f'Failed to get channel state {msg}. {err}')

    def is_channel_closed(self, channel: Union[int, str]):
        """ Check if {channel} (int) is closed. """
        return self.get_channel_state(channel) == 1

    def is_channel_open(self, channel: int):
        """ Check if {channel} (int) is open. """
        return self.get_channel_state(channel) == 0

    def open_all_channels(self, slot: Union[int, str] = 1, delay: float = 0):
        """ Open all channels for {slot} (int) w/ {delay} (Optional[float]). """
        for ch in range(self.num_channels):
            self.open_channel(ch)

    def close_all_channels(self, slot: Union[int, str] = 1, delay: float = 0):
        """Close all channels for {slot} (int) w/ {delay} (Optional[int]). """
        for ch in range(self.num_channels):
            self.close_channel(ch, delay)

    def open_channels(self, channels: List[Union[int, str]], delay: float = 0):
        """Open specified {channels} (List[int]) w/ {delay} (Optional[int]). """
        for ch in channels:
            self.open_channel(ch, delay)

    def close_channels(self, channels: List[Union[int, str]], delay: float = 0):
        """Close specified {channels} (List[int]) w/ {delay} (Optional[int]). """
        for ch in channels:
            self.close_channel(ch, delay)

    def set_channel(self, channel: Union[int, str], on: bool, delay: float, numAttempts: int = 3):
        """ Set specified {channel} (int) on or off w/ {delay}
            (Optional[int]) and {numAttempts} (int).
        """
        err = None
        for _ in range(numAttempts):
            try:
                self.write(f"relay {'on' if on else 'off'} {channel}")
                time.sleep(delay)
                if self.get_channel_state(channel) == on:
                    return
                self._clear_buffer()
            except Exception as e:
                err = e
        raise Exception(f"Failed to set channel {channel} {'on' if on else 'off'}. {err}")

    def open_channel(self, channel: Union[int, str], delay: float = 0):
        """ Open specified channel.
        Args:
            channel (int): Channel index
            delay (int, optional): Delay after operation (default 0).
        """
        self.set_channel(channel, on=False, delay=delay)

    def close_channel(self, channel: Union[int, str], delay: float = 0):
        """ Close specified channel.
        Args:
            channel (int): Channel index
            delay (int, optional): Delay after operation (default 0).
        """
        self.set_channel(channel, on=True, delay=delay)

    def read(self):
        """ Read from resource """
        if 'TCP' in self.device_type:
            return self.resource.read_until(
                f'{self.read_termination}>'.encode('ascii'), timeout=1
            ).decode()
        return self.resource.read_until(f'{self.read_termination}>'.encode('ascii')).decode()

    def write(self, cmd: str, reset_input: bool = True):
        """ Write cmd to resource."""
        self.resource.write(f'{cmd}{self.write_termination}'.encode('ascii'))
        if reset_input:
            time.sleep(0.1)
            self._clear_buffer()

    def query(self, cmd: str):
        """ Perform write followed by read."""
        self.write(cmd, reset_input=False)
        msg = self.read()
        msg = msg.replace(f'{cmd}\n{self.read_termination}', '')  # Remove sent cmd
        msg = msg.replace(f'{self.read_termination}>', '')  # Remove result term
        return msg

    def _clear_buffer(self):
        """Try to empty IO buffers. (useful when in unknown state)."""
        resource = self.resource
        if 'USB' in self.device_type and isinstance(resource, Serial):
            self.resource.reset_input_buffer()  # type: ignore
            self.resource.reset_output_buffer()  # type: ignore
