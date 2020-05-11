"""KeysightDAQ enables controlling various Keysight DAQs."""
from __future__ import print_function
from typing import List, Optional, Union
import time
from pyvisainstrument.VisaResource import VisaResource


class KeysightDAQ(VisaResource):
    """ KeysightDAQ enables controlling various Keysight DAQs."""

    def __init__(self, num_slots: int, num_channels: int, *args, **kwargs):
        super(KeysightDAQ, self).__init__(name='DAQ', *args, **kwargs)
        self.num_slots = num_slots
        self.num_channels = num_channels

    def is_channel_closed(self, channel: Union[int, str]):
        """ Get if channel is closed.
        Args:
            channel (int): Actuator with format SCC
        Returns:
            bool: True if channel is closed
        """
        return self.query(f'ROUT:CLOS? (@{int(channel):03d})') == '1'

    def is_channel_open(self, channel: Union[int, str]):
        """ Get if channel is open.
        Args:
            channel (int): Actuator with format SCC
        Returns:
            bool: True if channel is open
        """
        return not self.is_channel_closed(channel)

    def open_all_channels(self, slot: Union[int, str], delay: float = 0):
        """ Open all channels of a slot.
        Args:
            slot int: Slot (1-based)
        """
        for i in range(self.num_channels):
            ch = 100 * int(slot) + (i + 1)
            self.open_channel(ch, delay)

    def close_all_channels(self, slot: Union[int, str], delay: float = 0):
        """ Close all channels of a slot.
        Args:
            slot (Union[int, str]): Slot (1-based)
            delay (float, optional):
                Delay between each channel operation.
                Default is 0 - no delay
        """
        for i in range(self.num_channels):
            ch = 100 * int(slot) + (i + 1)
            self.close_channel(ch, delay)

    def open_channels(self, channels: List[Union[int, str]], delay: float = 0):
        """ Open specified channels.
        Args:
            channels ([Union[int, str]]):
                Channel indices with format SCC
            delay (int, optional):
                Delay between each channel operation.
                Default is 0 - no delay
        """
        for ch in channels:
            self.open_channel(ch, delay)

    def close_channels(self, channels: List[Union[int, str]], delay: float = 0):
        """ Close specified channels.
        Args:
            channels ([Union[int, str]]):
                Channel indices with format SCC
            delay (int, optional):
                Delay between each channel operation.
                Default is 0 - no delay
        """
        for ch in channels:
            self.close_channel(ch, delay)

    def open_channel(self, channel: Union[int, str], delay: float = 0):
        """ Open specified channel.
        Args:
            channel (Union[int, str]):
                Channel index with format SCC
            delay (int, optional):
                Delay after channel operation.
                Default is 0 - no delay
        """
        self.write(f'ROUT:OPEN (@{int(channel):03d})')
        time.sleep(delay)

    def close_channel(self, channel: Union[int, str], delay: float = 0):
        """ Close specified channel.
        Args:
            channel (Union[int, str]):
                Channel index with format SCC
            delay (int, optional):
                Delay after channel operation.
                Default is 0 - no delay
        """
        self.write(f'ROUT:CLOS (@{int(channel):03d})')
        time.sleep(delay)

    def measure_temperature(self, probe: str, probe_type: str, resolution: Optional[str] = None):
        """ Reset, configure, and measure temperature.
        Args:
            probe: {FRTD | RTD | FTHermistor | THERmistor | TCouple | DEF}
            probe_type:
                For FRTD and RTD: Type 85
                For FTHermistor and THERmistor: Type 2252, 5000, and 10,000
                For TCouple:Type B, E, J, K, N, R, S, and T
            resolution: Default 1 PLC
        Returns:
            float: temperature (°C is default unit)
        """
        return float(self.query(f'MEAS:TEMP? {probe},{probe_type}'))

    def measure_relative_humidity(self, probe: str, probe_type: str, resolution: Optional[str] = None):
        """ Reset, configure, and measure relative humidity.
            NOTE: This is not a standard SCPI command for DAQs.
        Args:
            probe: {FRTD | RTD | FTHermistor | THERmistor | TCouple | DEF}
            probe_type:
                For FRTD and RTD: Type 85
                For FTHermistor and THERmistor: Type 2252, 5000, and 10,000
                For TCouple:Type B, E, J, K, N, R, S, and T
            resolution: Default 1 PLC
        Returns:
            float: rel humidity (%)
        """
        return float(self.query(f'MEAS:RHumidity? {probe},{probe_type}'))

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
        bus_address='TCPIP::127.0.0.1::5020::SOCKET',
        num_slots=3,
        num_channels=20
    )
    daq.open(baud_rate=None, read_term='\n', write_term='\n')
    daq.open_all_channels(1)
    daq.open_channels([101, 103, 105])
    daq.close_channels([101, 103, 105])
    print("Finished")
