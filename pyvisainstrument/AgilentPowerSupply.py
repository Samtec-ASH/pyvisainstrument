"""AgilentPowerSupply is a convenience class to control various Agilent power supplies."""
from __future__ import print_function
from pyvisainstrument.VisaResource import VisaResource

# pylint: disable=too-many-public-methods
class AgilentPowerSupply(VisaResource):
    """AgilentPowerSupply is a convenience class to control various Agilent power supplies."""
    def __init__(self, *args, **kwargs):
        super(AgilentPowerSupply, self).__init__(name='PS', *args, **kwargs)

    def setChannel(self, ch):
        """Select channel for mult-channel PS.
        Args:
            ch (str, int): Channel name or index
        Returns:
            None
        """
        self.write('INST:SEL {0}'.format(ch))

    def getChannel(self):
        """Get selected channel for mult-channel PS.
        Args:
            None
        Returns:
            str: Selected channel
        """
        return str(self.query('INST:SEL?'))

    def enable(self):
        """Enable output state.
        Args:
            None
        Returns:
            None
        """
        self.setOutputState(True)

    def disable(self):
        """Disable output state.
        Args:
            None
        Returns:
            None
        """
        self.setOutputState(False)

    def apply(self, ch, volt, curr, precision=2):
        """Quickly apply power supply settings.
        Args:
            ch (str): Channel name
            volt (float): Voltage in volts
            curr (float): Current in amperes
            precision (int): Precision of voltage and current
        Returns:
            None
        """
        cmd = 'APPL {0}, {1:0.{3}f}, {2:0.{3}f}'.format(ch, volt, curr, precision)
        self.write(cmd)

    def setOutputState(self, state):
        """Enable or disable output.
        Args:
            state (bool): Output state
        Returns:
            None
        """
        self.write('OUTP:STAT ON' if state else 'OUTP:STAT OFF')

    def getOutputState(self):
        """Get output state.
        Args:
            None
        Returns:
            state (bool): Output state
        """
        return self.query('OUTP:STAT?') == '1'

    def setVoltageSetPoint(self, voltage, precision=2):
        """Set voltage setpoint
        Args:
            volt (float): Voltage in volts
            precision (int): Precision of voltage
        Returns:
            None
        """
        self.write('VOLT {1:0.{0}f}'.format(precision, voltage))

    def getVoltageSetPoint(self):
        """Get voltage setpoint
        Args:
            None
        Returns:
            float: Voltage in volts
        """
        return float(self.query('VOLT?'))

    def setCurrentLimit(self, current, precision=2):
        """Set current limit
        Args:
            current (float): Current in amperes
            precision (int): Precision of current
        Returns:
            None
        """
        self.write('CURR {1:0.{0}f}'.format(precision, current))

    def getCurrentLimit(self):
        """Get current limit
        Args:
            None
        Returns:
            float: Current in amperes
        """
        return float(self.query('CURR?'))

    def getMeasuredVoltage(self):
        """Get measured voltage
        Args:
            None
        Returns:
            float: Measured voltage in volts
        """
        return float(self.query('MEAS:VOLT:DC?'))

    def getMeasuredCurrent(self):
        """Get measured current usage
        Args:
            None
        Returns:
            float: Measured current in amperes
        """
        return float(self.query('MEAS:CURR:DC?'))

    def getMaxVoltage(self):
        """Get max voltage of PS channel
        Args:
            None
        Returns:
            float: Max voltage in volts
        """
        return float(self.query('VOLT? MAX'))

    def getMinVoltage(self):
        """Get min voltage of PS channel
        Args:
            None
        Returns:
            float: Min voltage in volts
        """
        return float(self.query('VOLT? MIN'))

    def getMaxCurrentLimit(self):
        """Get max current limit of PS channel
        Args:
            None
        Returns:
            float: Max current limit in amperes
        """
        return float(self.query('CURR? MAX'))

    def getMinCurrentLimit(self):
        """Get min current limit of PS channel
        Args:
            None
        Returns:
            float: Min current limit in amperes
        """
        return float(self.query('CURR? MIN'))

    def setDisplayText(self, txt):
        """Set display text
        Args:
            txt (str): Text to display
        Returns:
            None
        """
        self.write('DISP:TEXT:DATA \"{0}\"'.format(txt))

    def clearDisplayText(self):
        """Clear display text
        Args:
            None
        Returns:
            None
        """
        self.write('DISP:TEXT:CLEA')

    def getDisplayText(self):
        """Get display text
        Args:
            None
        Returns:
            str: Text to display
        """
        return str(self.query('DISP:TEXT:DATA?'))


if __name__ == '__main__':
    print('Started')
    ps = AgilentPowerSupply(busAddress='TCPIP::127.0.0.1::5020::SOCKET')
    ps.open()
    ps.setChannel(1)
    ps.enable()
    ps.setCurrentLimit(2)
    ps.setVoltageSetPoint(5.0)
    print(ps.getCurrentLimit())
    print(ps.getVoltageSetPoint())
    ps.disable()
    print('Finished')
