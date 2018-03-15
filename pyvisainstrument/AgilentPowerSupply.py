
"""AgilentPowerSupply is a convience class to control various Agilent power supplies
via SCPI.
"""

from __future__ import print_function
from pyvisainstrument.GPIBLink import GPIBLinkResource

# pylint: disable=too-many-public-methods
class AgilentPowerSupply(GPIBLinkResource):
    """AgilentPowerSupply is a convience class to control various Agilent
    power supplies via SCPI.

    Attributes:
        None
    """
    def __init__(self, busLinkAddress, verbose=False):
        super(AgilentPowerSupply, self).__init__(busAddress=busLinkAddress)
        self.verbose = verbose

    # pylint: disable=arguments-differ,useless-super-delegation
    def open(self, *args, **kwargs):
        """Open instrument connection.
        Args:
            None
        Returns:
            None
        """
        super(AgilentPowerSupply, self).open(*args, **kwargs)

    # pylint: disable=arguments-differ,useless-super-delegation
    def close(self):
        """Close instrument connection.
        Args:
            None
        Returns:
            None
        """
        super(AgilentPowerSupply, self).close()

    def getID(self):
        """Get identifier.
        Args:
            None
        Returns:
            str: ID
        """
        return str(self._querySCPI("*IDN?"))

    def setChannel(self, ch):
        """Select channel for mult-channel PS.
        Args:
            ch (str, int): Channel name or index
        Returns:
            None
        """
        cmd = str.format("INST:SEL {:s}", str(ch))
        self._writeSCPI(cmd)

    def getChannel(self):
        """Get selected channel for mult-channel PS.
        Args:
            None
        Returns:
            str: Selected channel
        """
        cmd = "INST:SEL?"
        rst = str(self._querySCPI(cmd))
        return rst

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
        cmd = str.format("APPL {0:s}, {1:0.{3}f}, {2:0.{3}f}", ch, volt, curr, precision)
        self._writeSCPI(cmd)

    def setOutputState(self, state):
        """Enable or disable output.
        Args:
            state (bool): Output state
        Returns:
            None
        """
        cmd = "OUTP:STAT ON" if state else "OUTP:STAT OFF"
        self._writeSCPI(cmd)

    def getOutputState(self):
        """Get output state.
        Args:
            None
        Returns:
            state (bool): Output state
        """
        cmd = "OUTP:STAT?"
        rst = self._querySCPI(cmd)
        return rst == '1'

    def setVoltageSetPoint(self, voltage, precision=2):
        """Set voltage setpoint
        Args:
            volt (float): Voltage in volts
            precision (int): Precision of voltage
        Returns:
            None
        """
        cmd = str.format("VOLT {1:0.{0}f}", precision, voltage)
        self._writeSCPI(cmd)

    def getVoltageSetPoint(self):
        """Get voltage setpoint
        Args:
            None
        Returns:
            float: Voltage in volts
        """
        cmd = "VOLT?"
        rst = float(self._querySCPI(cmd))
        return rst

    def setCurrentLimit(self, current, precision=2):
        """Set current limit
        Args:
            current (float): Current in amperes
            precision (int): Precision of current
        Returns:
            None
        """
        cmd = str.format("CURR {1:0.{0}f}", precision, current)
        self._writeSCPI(cmd)

    def getCurrentLimit(self):
        """Get current limit
        Args:
            None
        Returns:
            float: Current in amperes
        """
        cmd = "CURR?"
        rst = float(self._querySCPI(cmd))
        return rst

    def getMeasuredVoltage(self):
        """Get measured voltage
        Args:
            None
        Returns:
            float: Measured voltage in volts
        """
        cmd = "MEAS:VOLT:DC?"
        rst = float(self._querySCPI(cmd))
        return rst

    def getMeasuredCurrent(self):
        """Get measured current usage
        Args:
            None
        Returns:
            float: Measured current in amperes
        """
        cmd = "MEAS:CURR:DC?"
        rst = float(self._querySCPI(cmd))
        return rst

    def getMaxVoltage(self):
        """Get max voltage of PS channel
        Args:
            None
        Returns:
            float: Max voltage in volts
        """
        cmd = "VOLT? MAX"
        rst = float(self._querySCPI(cmd))
        return rst

    def getMinVoltage(self):
        """Get min voltage of PS channel
        Args:
            None
        Returns:
            float: Min voltage in volts
        """
        cmd = "VOLT? MIN"
        rst = float(self._querySCPI(cmd))
        return rst

    def getMaxCurrentLimit(self):
        """Get max current limit of PS channel
        Args:
            None
        Returns:
            float: Max current limit in amperes
        """
        cmd = "CURR? MAX"
        rst = float(self._querySCPI(cmd))
        return rst

    def getMinCurrentLimit(self):
        """Get min current limit of PS channel
        Args:
            None
        Returns:
            float: Min current limit in amperes
        """
        cmd = "CURR? MIN"
        rst = float(self._querySCPI(cmd))
        return rst

    def setDisplayText(self, txt):
        """Set display text
        Args:
            txt (str): Text to display
        Returns:
            None
        """
        cmd = str.format("DISP:TEXT:DATA \"{:s}\"", txt)
        self._writeSCPI(cmd)

    def clearDisplayText(self):
        """Clear display text
        Args:
            None
        Returns:
            None
        """
        cmd = "DISP:TEXT:CLEA"
        self._writeSCPI(cmd)

    def getDisplayText(self):
        """Get display text
        Args:
            None
        Returns:
            str: Text to display
        """
        cmd = "DISP:TEXT:DATA?"
        rst = str(self._querySCPI(cmd))
        return rst

    def _querySCPI(self, scpiStr):
        """Perform raw SCPI query
        Args:
            scpiStr (str): SCPI query
        Returns:
            str: Query result
        """
        rst = self.query(scpiStr)
        if self.verbose:
            print(str.format("PS.query({:s}) -> {:s}", scpiStr, rst))
        return rst

    def _writeSCPI(self, scpiStr):
        """Perform raw SCPI write
        Args:
            scpiStr (str): SCPI command
        Returns:
            None
        """
        if self.verbose:
            print(str.format("PS.write({:s})", scpiStr))
        self.write(scpiStr)


if __name__ == '__main__':
    print("Starting")
    ps = AgilentPowerSupply("TCPIP::127.0.0.1::5020::SOCKET")
    ps.open()
    ps.setChannel(1)
    ps.enable()
    ps.setCurrentLimit(2)
    ps.setVoltageSetPoint(5.0)
    print(ps.getCurrentLimit())
    print(ps.getVoltageSetPoint())
    ps.disable()
    print("Finished")
