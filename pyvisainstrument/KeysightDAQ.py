"""KeysightDAQ is a convenience class to control various Keysight Switch DAQs."""
from __future__ import print_function
from typing import List
import time
from pyvisainstrument.VisaResource import VisaResource


class KeysightDAQ(VisaResource):
    """KeysightDAQ is a convenience class to control various Keysight Switch DAQs."""

    def __init__(self, num_slots, num_channels, *args, **kwargs):
        super(KeysightDAQ, self).__init__(name='DAQ', *args, **kwargs)
        self.num_slots = num_slots
        self.num_channels = num_channels

    def is_channel_closed(self, channel: int):
        """Get if channel is closed.
        Args:
            channel (int): Actuator with format SCC
        Returns:
            bool: True if channel is closed
        """
        return self.query(f'ROUT:CLOS? (@{channel:03d})') == '1'

    def is_channel_open(self, channel: int):
        """Get if channel is open.
        Args:
            channel (int): Actuator with format SCC
        Returns:
            bool: True if channel is open
        """
        return not self.is_channel_closed(channel)

    def open_all_channels(self, slot: int, delay=0):
        """Open all channels of a slot.
        Args:
            slot int: Slot (1-based)
        """
        for i in range(self.num_channels):
            ch = 100 * slot + (i + 1)
            self.open_channel(ch)
            time.sleep(delay)

    def close_all_channels(self, slot: int, delay: float = 0):
        """Close all channels of a slot.
        Args:
            slot (int): Slot (1-based)
            delay (float, optional):
                Delay between each channel operation.
                Default is 0 - no delay
        """
        for i in range(self.num_channels):
            ch = 100 * slot + (i + 1)
            self.close_channel(ch, delay)

    def open_channels(self, channels: List[int], delay: float = 0):
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
            self.open_channel(ch, delay)

    def close_channels(self, channels: List[int], delay: float = 0):
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
            self.close_channel(ch, delay)

    def open_channel(self, channel: int, delay: float = 0):
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
        self.write(f'ROUT:OPEN (@{channel:03d})')
        time.sleep(delay)

    def close_channel(self, channel: int, delay: float = 0):
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
        self.write(f'ROUT:CLOS (@{channel:03d})')
        time.sleep(delay)

    def wait_for_completion(self, timeout: float = 2):
        """Wait for physical operation to complete.
        Args:
            timeout (float):
                Max time to wait for completion in secs.
        Returns:
            Exception if timeout reached
        """
        done = False
        wait_time = 0.0
        while not done:
            time.sleep(15E-3)
            done_str = self.resource.query('ROUT:DONE?', delay=15E-3)
            if isinstance(done_str, str) and done_str.strip().isnumeric():
                done = int(done_str.strip())
            wait_time += 15E-3
            if wait_time >= timeout:
                raise Exception('Timeout occurred waiting for route to finish.')


if __name__ == '__main__':
    print('Started')
    daq = KeysightDAQ(
        busAddress='TCPIP::127.0.0.1::5020::SOCKET',
        num_slots=3,
        num_channels=20
    )
    daq.open(baud_rate=None, read_term='\n', write_term='\n')
    daq.open_all_channels(1)
    daq.open_channels([101, 103, 105])
    daq.close_channels([101, 103, 105])
    print("Finished")
