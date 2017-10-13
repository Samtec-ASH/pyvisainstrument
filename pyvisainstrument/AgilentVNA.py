import time
import numpy as np
from pyvisainstrument.GPIBLink import GPIBLinkResource


class AgilentVNA(GPIBLinkResource):
    """Represent Agilent 4-port Vector Network Analyzer."""

    def __init__(self, busLinkAddress):
        """Init function."""
        super(AgilentVNA, self).__init__(busAddress=busLinkAddress)
        self.busLinkAddress = busLinkAddress

    def open(self, termChar='\n'):
        """Open resouce link for communication."""
        super(AgilentVNA, self).open()
        if termChar:
            self.resource.read_termination = termChar

    def close(self):
        """Close resouce link for communication."""
        super(AgilentVNA, self).close()

    def getID(self):
        return str(self._querySCPI("*IDN?"))

    def _writeSCPI(self, scpiStr):
        print(str.format("VNA.write({:s})", scpiStr))
        self.write(scpiStr)

    def _querySCPI(self, scpiStr):
        print(str.format("VNA.query({:s})", scpiStr))
        rst = self.query(scpiStr)
        print(str.format("VNA.query({:s}) -> {:s}", scpiStr, rst))
        return rst

    def setStartFreq(self, channel, freq_hz):
        cmd = str.format("SENSE{:d}:FREQUENCY:START {:.0f}", channel, freq_hz)
        self._writeSCPI(cmd)

    def getStartFreq(self, channel):
        cmd = str.format("SENSE{:d}:FREQUENCY:START?", channel)
        rst = float(self._querySCPI(cmd))
        return rst

    def setStopFreq(self, channel, freq_hz):
        cmd = str.format("SENSE{:d}:FREQUENCY:STOP {:.0f}", channel, freq_hz)
        self._writeSCPI(cmd)

    def getStopFreq(self, channel):
        cmd = str.format("SENSE{:d}:FREQUENCY:STOP?", channel)
        rst = float(self._querySCPI(cmd))
        return rst

    def setCenterFreq(self, channel, freq_hz):
        cmd = str.format("SENSE{:d}:FREQUENCY:CENT {:.0f}", channel, freq_hz)
        self._writeSCPI(cmd)

    def getCenterFreq(self, channel):
        cmd = str.format("SENSE{:d}:FREQUENCY:CENT?", channel)
        rst = float(self._querySCPI(cmd))
        return rst

    def setCWFreq(self, channel, freq_hz):
        cmd = str.format("SENSE{:d}:FREQUENCY:CW {:.0f}", channel, freq_hz)
        self._writeSCPI(cmd)

    def getCWFreq(self, channel):
        cmd = str.format("SENSE{:d}:FREQUENCY:CW?", channel)
        rst = float(self._querySCPI(cmd))
        return rst

    def setNumberSweepPoints(self, channel, numPoints):
        cmd = str.format("SENSE{:d}:SWEEP:POINTS {:d}", channel, numPoints)
        self._writeSCPI(cmd)

    def getNumberSweepPoints(self, channel):
        cmd = str.format("SENSE{:d}:SWEEP:POINTS?", channel)
        rst = int(self._querySCPI(cmd))
        return rst

    def setFrequencyStepSize(self, channel, freq_hz):
        cmd = str.format("SENSE{:d}:SWEEP:STEP {1:0.}", channel, freq_hz)
        self._writeSCPI(cmd)

    def getFrequencyStepSize(self, channel):
        cmd = str.format("SENSE{:d}:SWEEP:STEP?", channel)
        rst = float(self._querySCPI(cmd))
        return rst

    def setSweepType(self, channel, type):
        # Types = ["LINEAR", "LOGARITHMIC", "POWER", "CW", "SEGMENT", "PHASE"]
        cmd = str.format("SENSE{:d}:SWEEP:TYPE {:s}", channel, type)
        self._writeSCPI(cmd)

    def getSweepType(self, channel):
        cmd = str.format("SENSE{:d}:SWEEP:TYPE?", channel)
        rst = str(self._querySCPI(cmd))
        return rst

    def setSweepPower(self, channel, power):
        cmd = str.format("SENSE{:d}:SWEEP:POWER {:d}", channel, power)
        self._writeSCPI(cmd)

    def getSweepPower(self, channel):
        cmd = str.format("SENSE{:d}:SWEEP:POWER", channel)
        rst = int(self._querySCPI(cmd))
        return rst

    def setCalibration(self, calStr, channel=1):
        cmd = str.format("SENSE{:d}:CORR:CSET:ACT '{:s}',1", channel, calStr)
        self._writeSCPI(cmd)

    def setupSweep(self, channel, startFreq, stopFreq, numPoints,
                   sweepType="LINEAR"):
        self.setStartFreq(channel, startFreq)
        self.setStopFreq(channel, stopFreq)
        self.setNumberSweepPoints(channel, numPoints)
        self.setSweepType(channel, sweepType)

    def setupS4PTraces(self):
        # Delete all measurements
        self._writeSCPI("CALC1:PAR:DEL:ALL")
        self._writeSCPI("CALC1:FSIM:BAL:DEV BBALANCED")
        self._writeSCPI("CALC1:PAR:DEL:ALL")

        self._writeSCPI("DISP:WIND1:STATE ON")
        self._writeSCPI("DISP:WIND2:STATE ON")
        self._writeSCPI("DISP:WIND3:STATE ON")
        self._writeSCPI("DISP:WIND4:STATE ON")

        # Now create logical port 1 reflection parameters
        self._writeSCPI("CALC1:PAR:DEF 'sdd11',S11")
        self._writeSCPI("CALC1:PAR:SEL 'sdd11'")
        self._writeSCPI("CALC1:FSIM:BAL:PAR:STATE ON")
        self._writeSCPI("CALC1:FSIM:BAL:PAR:BBAL:DEF SDD11")
        self._writeSCPI("DISP:WIND1:TRAC1:FEED 'sdd11'")
        #self._writeSCPI("DISP:WIND1:Y:AUTO")

        # Now create reverse transmission parameters
        self._writeSCPI("CALC1:PAR:DEF 'sdd12',S11")
        self._writeSCPI("CALC1:PAR:SEL 'sdd12'")
        self._writeSCPI("CALC1:FSIM:BAL:PAR:STATE ON")
        self._writeSCPI("CALC1:FSIM:BAL:PAR:BBAL:DEF SDD12")
        self._writeSCPI("DISP:WIND2:TRAC2:FEED 'sdd12'")
        #self._writeSCPI("DISP:WIND2:Y:AUTO")

        # Create a trace called "sdd21" and for that trace turn on the balanced
        # transformation and set the balanced transformation to BBAL SDD21.
        self._writeSCPI("CALC1:PAR:DEF 'sdd21',S11")
        self._writeSCPI("CALC1:PAR:SEL 'sdd21'")
        self._writeSCPI("CALC1:FSIM:BAL:PAR:STATE ON")
        self._writeSCPI("CALC1:FSIM:BAL:PAR:BBAL:DEF SDD21")
        self._writeSCPI("DISP:WIND3:TRAC3:FEED 'sdd21'")
        #self._writeSCPI("DISP:WIND3:Y:AUTO")

        # Now create reverse reflection parameters
        self._writeSCPI("CALC1:PAR:DEF 'sdd22',S11")
        self._writeSCPI("CALC1:PAR:SEL 'sdd22'")
        self._writeSCPI("CALC1:FSIM:BAL:PAR:STATE ON")
        self._writeSCPI("CALC1:FSIM:BAL:PAR:BBAL:DEF SDD22")
        self._writeSCPI("DISP:WIND4:TRAC4:FEED 'sdd22'")
        #self._writeSCPI("DISP:WIND4:Y:AUTO")

        self._writeSCPI("CALC1:FSIM:BAL:DEV BBALANCED")
        self._writeSCPI("CALC1:FSIM:BAL:TOP:BBAL:PPORTS 1,2,3,4")

        self._writeSCPI("TRIG:SOUR IMMediate")

    def captureS4PTrace(self, dtype=float):

        # Trigger trace and wait.
        isRunning = True
        while isRunning:
            msg = self._querySCPI("SENSE1:SWEEP:MODE SINGle;*OPC?")
            isRunning = (int(msg) == 0)
            time.sleep(0.01)

        s4Dict = dict(sdd11=None, sdd12=None, sdd21=None, sdd22=None)
        dtypeName = "SDATA" if dtype == complex else "FDATA"
        dataQuery = str.format("CALC1:DATA? {:s}", dtypeName)
        for s4Name in s4Dict.keys():
            cmd = str.format("CALC1:PAR:SEL '{:s}'", s4Name)
            self._writeSCPI(cmd)
            data = self.resource.query_ascii_values(dataQuery, container=np.array).squeeze()
            # Complex is returned as alternating real,imag,...
            if dtype == complex:
                data = data.view(dtype=complex)
            s4Dict[s4Name] = data

        # Combine into 2x2xNUM_POINTS tensor
        s4Data = np.zeros((2, 2, s4Dict['sdd11'].size), dtype=dtype)
        s4Data[0, 0] = s4Dict['sdd11']
        s4Data[0, 1] = s4Dict['sdd12']
        s4Data[1, 0] = s4Dict['sdd21']
        s4Data[1, 1] = s4Dict['sdd22']
        return s4Data

    def setupECalibration(self, channel, startFreq, stopFreq, numPoints, sweepType):
        """ Perform 4-port calibration w/ 2-port e-cal module (N4692-60001 ECal 13226)."""
        self.setupSweep(channel, startFreq, stopFreq, numPoints, sweepType)

        cmd = "SENSE1:corr:coll:guid:conn:port"
        fport = "2.92 mm female"
        mport = "2.92 mm male"
        self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, 1, fport))
        self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, 2, fport))
        self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, 3, fport))
        self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, 4, fport))

        cmd = "SENSE1:corr:coll:guid:ckit:port"
        kit = "N4692-60003 ECal 13226"
        self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, 1, kit))
        self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, 2, kit))
        self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, 3, kit))
        self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, 4, kit))

        self._writeSCPI("SENSE1:corr:pref:ecal:ori ON")

        '''
        ' If your selected cal kit is not a 4-port ECal module which can
        ' mate to all 4 ports at once, then you may want to choose which
        ' thru connections to measure for the cal.  You must measure at
        ' least 3 different thru paths for a 4-port cal (for greatest
        ' accuracy you can choose to measure a thru connection for all 6
        ' pairings of the 4 ports).  If you omit this command, the default
        ' is to measure from port 1 to port 2, port 1 to port 3, and
        ' port 1 to port 4. 1,3,1,4,2,4,2,3.
        '''
        self._writeSCPI("SENSE1:corr:coll:guid:init")
        self._writeSCPI("SENSE1:corr:coll:guid:thru:ports 1,3,1,4,2,4,2,3")
        self._writeSCPI("SENSE1:corr:coll:guid:init")

    def getNumberECalibrationSteps(self):
        """ Must call setupECalibration() before calling this. """
        return int(self._querySCPI("SENSE1:corr:coll:guid:steps?"))

    def getECalibrationStepDescription(self, step):
        """ Must call setupECalibration() before calling this. """
        return self._querySCPI(str.format("SENSE1:corr:coll:guid:desc? {:d}", step+1))

    def performECalibrationStep(self, step, save=True):
        """ Must call setupECalibration() before calling this. """
        if step >= self.getNumberECalibrationSteps():
            return
        self._writeSCPI(str.format("SENSE1:corr:coll:guid:acq STAN{:d}", step+1))
        time.sleep(15)
        if step == (self.getNumberECalibrationSteps()-1):
            self._writeSCPI("SENSE1:corr:coll:guid:save")

    def performECalibrationSteps(self):
        """ This performs all steps as an iterator.
        Must call setupECalibration() before calling this.
        >>> vna.setupECalibration(...)
        >>> for stepDescription in vna.performECalibrationSteps():
        >>>     print(stepDescription)
        """
        numSteps = self.getNumberECalibrationSteps()
        i = 0
        while i < numSteps:
            msg = self.getECalibrationStepDescription(i)
            yield msg
            self.performECalibrationStep(i, save=True)
            i += 1


if __name__ == '__main__':
    print("Starting")
    vna = AgilentVNA("TCPIP::127.0.0.1::5020::SOCKET")
    vna.open(termChar='\n')
    print(vna.getID())
    vna.setupSweep(1, 20E6, 30E6, 10, "LINEAR")
    vna.setupS4PTraces()
    print(vna.captureS4PTrace())
    vna.close()
    print("Finished")
