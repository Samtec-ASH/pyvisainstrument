""" KeysightPSU enables controlling various Keysight power supply units."""
from __future__ import print_function
from typing import Union
from pyvisainstrument.VisaResource import VisaResource


class KeysightPSU(VisaResource):
    """ KeysightPSU enables controlling various Keysight power supply units."""

    def __init__(self, *args, **kwargs):
        super(KeysightPSU, self).__init__(name='PS', *args, **kwargs)

    def set_channel(self, ch: Union[str, int]):
        """ Select channel for multi-channel PS.
        Args:
            ch (str, int): Channel name or index
        """
        self.write(f'INST:SEL {ch}')

    def get_channel(self):
        """ Get selected channel for multi-channel PS.
        Args:
            None
        Returns:
            str: Selected channel
        """
        return str(self.query('INST:SEL?'))

    def enable(self):
        """ Enable output state of selected channel. """
        self.set_output_state(True)

    def disable(self):
        """ Disable output state of selected channel. """
        self.set_output_state(False)

    def apply(self, ch: Union[str, int], volt: float, curr: float, precision: int = 2):
        """ Quickly apply power supply settings.
        Args:
            ch (str): Channel name
            volt (float): Voltage in volts
            curr (float): Current in amperes
            precision (int): Precision of voltage and current
        """
        self.write(f'APPL {ch}, {volt:0.{precision}f}, {curr:0.{precision}f}')

    def set_output_state(self, state: bool):
        """ Enable or disable output.
        Args:
            state (bool): Output state
        """
        self.write(f"OUTP:STAT {'ON' if state else 'OFF'}")

    def get_output_state(self):
        """ Get output state.
        Args:
            None
        Returns:
            state (bool): Output state
        """
        return self.query('OUTP:STAT?') == '1'

    def set_voltage_set_point(self, voltage: float, precision: int = 2):
        """ Set voltage set point
        Args:
            volt (float): Voltage in volts
            precision (int): Precision of voltage
        """
        self.write(f'VOLT {voltage:0.{precision}f}')

    def get_voltage_set_point(self):
        """ Get voltage set point
        Args:
            None
        Returns:
            float: Voltage in volts
        """
        return float(self.query('VOLT?'))

    def set_current_limit(self, current: float, precision: int = 2):
        """ Set current limit
        Args:
            current (float): Current in amperes
            precision (int): Precision of current
        """
        self.write(f'CURR {current:0.{precision}f}')

    def get_current_limit(self):
        """ Get current limit
        Args:
            None
        Returns:
            float: Current in amperes
        """
        return float(self.query('CURR?'))

    def get_measured_voltage(self):
        """ Get measured voltage
        Args:
            None
        Returns:
            float: Measured voltage in volts
        """
        return float(self.query('MEAS:VOLT:DC?'))

    def get_measured_current(self):
        """ Get measured current usage
        Args:
            None
        Returns:
            float: Measured current in amperes
        """
        return float(self.query('MEAS:CURR:DC?'))

    def get_max_voltage(self):
        """ Get max voltage of PS channel
        Args:
            None
        Returns:
            float: Max voltage in volts
        """
        return float(self.query('VOLT? MAX'))

    def get_min_voltage(self):
        """ Get min voltage of PS channel
        Args:
            None
        Returns:
            float: Min voltage in volts
        """
        return float(self.query('VOLT? MIN'))

    def get_max_current_limit(self):
        """ Get max current limit of PS channel
        Args:
            None
        Returns:
            float: Max current limit in amperes
        """
        return float(self.query('CURR? MAX'))

    def get_min_current_limit(self):
        """ Get min current limit of PS channel
        Args:
            None
        Returns:
            float: Min current limit in amperes
        """
        return float(self.query('CURR? MIN'))

    def set_display_text(self, txt: str):
        """ Set display text
        Args:
            txt (str): Text to display
        """
        self.write(f'DISP:TEXT:DATA \"{txt}\"')

    def clear_display_text(self):
        """ Clear display text
        Args:
            None
        """
        self.write('DISP:TEXT:CLEA')

    def get_display_text(self):
        """ Get display text
        Args:
            None
        Returns:
            str: Text on display
        """
        return str(self.query('DISP:TEXT:DATA?'))


if __name__ == '__main__':
    print('Started')
    ps = KeysightPSU(bus_address='TCPIP::127.0.0.1::5020::SOCKET')
    ps.open()
    ps.set_channel(1)
    ps.enable()
    ps.set_current_limit(2)
    ps.set_voltage_set_point(5.0)
    print(ps.get_current_limit())
    print(ps.get_voltage_set_point())
    ps.disable()
    print('Finished')
