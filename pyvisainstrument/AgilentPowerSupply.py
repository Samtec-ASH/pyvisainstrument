
from pyvisainstrument.GPIBLink import GPIBLinkResource


class AgilentPowerSupply(GPIBLinkResource):

    def __init__(self, busLinkAddress):
        """Initialize Agilint Power Supply."""
        super(AgilentPowerSupply, self).__init__(busAddress=busLinkAddress)

    def open(self, baudRate=None, readTerm=None, writeTerm=None):
        super(AgilentPowerSupply, self).open()
        if baudRate:
            self.resource.baud_rate = baudRate
        if readTerm:
            self.resource.read_termination = readTerm
        if writeTerm:
            self.resource.write_termination = writeTerm

    def close(self):
        super(AgilentPowerSupply, self).close()

    def getID(self):
        return str(self._querySCPI("*IDN?"))

    def setChannel(self, ch):
        cmd = str.format("INST:SEL {:s}", str(ch))
        self._writeSCPI(cmd)

    def getChannel(self):
        cmd = "INST:SEL?"
        rst = str(self._querySCPI(cmd))
        return rst

    def enable(self):
        self.setOutputState(True)

    def disable(self):
        self.setOutputState(False)

    def setOutputState(self, state):
        cmd = "OUTP:STAT ON" if state else "OUTP:STAT OFF"
        self._writeSCPI(cmd)

    def getOutputState(self):
        cmd = "OUTP:STAT?"
        rst = bool(self._querySCPI(cmd))
        return rst

    def setVoltageSetPoint(self, voltage, precision=2):
        cmd = str.format("VOLT {1:0.{0}f}", precision, voltage)
        self._writeSCPI(cmd)

    def getVoltageSetPoint(self):
        cmd = "VOLT?"
        rst = float(self._querySCPI(cmd))
        return rst

    def setCurrentLimit(self, current, precision=2):
        cmd = str.format("CURR {1:0.{0}f}", precision, current)
        self._writeSCPI(cmd)

    def getCurrentLimit(self):
        cmd = "CURR?"
        rst = float(self._querySCPI(cmd))
        return rst

    def getMeasuredVoltage(self):
        cmd = "MEAS:VOLT:DC?"
        rst = float(self._querySCPI(cmd))
        return rst

    def getMeasuredCurrent(self):
        cmd = "MEAS:CURR:DC?"
        rst = float(self._querySCPI(cmd))
        return rst

    def getMaxVoltage(self):
        cmd = "VOLT? MAX"
        rst = float(self._querySCPI(cmd))
        return rst

    def getMinVoltage(self):
        cmd = "VOLT? MIN"
        rst = float(self._querySCPI(cmd))
        return rst

    def getMaxCurrentLimit(self):
        cmd = "CURR? MAX"
        rst = float(self._querySCPI(cmd))
        return rst

    def getMinCurrentLimit(self):
        cmd = "CURR? MIN"
        rst = float(self._querySCPI(cmd))
        return rst

    def setDisplayText(self, txt):
        cmd = str.format("DISP:TEXT:DATA \"{:s}\"", txt)
        self._writeSCPI(cmd)

    def clearDisplayText(self, txt):
        cmd = "DISP:TEXT:CLEA"
        self._writeSCPI(cmd)

    def getDisplayText(self):
        cmd = "DISP:TEXT:DATA?"
        rst = str(self._querySCPI(cmd))
        return rst

    def _querySCPI(self, scpiStr):
        print(str.format("PS.query({:s})", scpiStr))
        return self.query(scpiStr)

    def _writeSCPI(self, scpiStr):
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
