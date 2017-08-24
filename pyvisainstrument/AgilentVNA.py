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
        if termChar is not None:
            self.resource.read_termination = termChar

    def close(self):
        """Close resouce link for communication."""
        super(AgilentVNA, self).close()

    def getID(self):
        return str(self._querySCPI("*IDN?"))

    def _writeSCPI(self, scpiStr):
        self.write(scpiStr)

    def _querySCPI(self, scpiStr):
        return self.query(scpiStr)

    def setStartFreq(self, channel, freq_hz):
        cmd = str.format("SENS{:d}:FREQ:STAR {:.0f}", channel, freq_hz)
        self._writeSCPI(cmd)

    def getStartFreq(self, channel):
        cmd = str.format("SENS{:d}:FREQ:STAR?", channel)
        rst = float(self._querySCPI(cmd))
        return rst

    def setStopFreq(self, channel, freq_hz):
        cmd = str.format("SENS{:d}:FREQ:STOP {:.0f}", channel, freq_hz)
        self._writeSCPI(cmd)

    def getStopFreq(self, channel):
        cmd = str.format("SENS{:d}:FREQ:STOP?", channel)
        rst = float(self._querySCPI(cmd))
        return rst

    def setCenterFreq(self, channel, freq_hz):
        cmd = str.format("SENS{:d}:FREQ:CENT {:.0f}", channel, freq_hz)
        self._writeSCPI(cmd)

    def getCenterFreq(self, channel):
        cmd = str.format("SENS{:d}:FREQ:CENT?", channel)
        rst = float(self._querySCPI(cmd))
        return rst

    def setCWFreq(self, channel, freq_hz):
        cmd = str.format("SENS{:d}:FREQ:CW {:.0f}", channel, freq_hz)
        self._writeSCPI(cmd)

    def getCWFreq(self, channel):
        cmd = str.format("SENS{:d}:FREQ:CW?", channel)
        rst = float(self._querySCPI(cmd))
        return rst

    def setNumberSweepPoints(self, channel, numPoints):
        cmd = str.format("SENS{:d}:SWEE:POIN {:d}", channel, numPoints)
        self._writeSCPI(cmd)

    def getNumberSweepPoints(self, channel):
        cmd = str.format("SENS{:d}:SWEE:POIN?", channel)
        rst = int(self._querySCPI(cmd))
        return rst

    def setFrequencyStepSize(self, channel, freq_hz):
        cmd = str.format("SENS{:d}:SWEE:STEP {1:0.}", channel, freq_hz)
        self._writeSCPI(cmd)

    def getFrequencyStepSize(self, channel):
        cmd = str.format("SENS{:d}:SWEE:STEP?", channel)
        rst = float(self._querySCPI(cmd))
        return rst

    def setSweepType(self, channel, type):
        # Types = ["LINEAR", "LOGARITHMIC", "POWER", "CW", "SEGMENT", "PHASE"]
        cmd = str.format("SENS{:d}:SWEE:TYPE {:s}", channel, type)
        self._writeSCPI(cmd)

    def getSweepType(self, channel):
        cmd = str.format("SENS{:d}:SWEE:TYPE?", channel)
        rst = str(self._querySCPI(cmd))
        return rst

    def setSweepPower(self, channel, power):
        cmd = str.format("SENS{:d}:SWEE:POWE {:d}", channel, power)
        self._writeSCPI(cmd)

    def getSweepPower(self, channel):
        cmd = str.format("SENS{:d}:SWEE:POWE", channel)
        rst = int(self._querySCPI(cmd))
        return rst

    def setCalibration(self, calStr, channel=1):
        cmd = str.format("SENS{:d}:CORR:CSET:ACT '{:s}',1", channel, calStr)
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
        self._writeSCPI("CALC1:FSIM:BAL:DEV BBALanced")
        self._writeSCPI("CALC1:FSIM:BAL:TOP:BBAL:PPOR 1,3,2,4")

        # Now create logical port 1 reflection parameters
        self._writeSCPI("CALC1:PAR:DEF 'sdd11',S11")
        self._writeSCPI("CALC1:PAR:SEL 'sdd11'")
        self._writeSCPI("CALC1:FSIM:BAL:PAR:STAT ON")
        self._writeSCPI("CALC1:FSIM:BAL:PAR:BBAL:DEF SDD11")
        self._writeSCPI("DISP:WIND1:TRAC1:FEED 'sdd11'")
        # Now create reverse transmission parameters
        self._writeSCPI("CALC1:PAR:DEF 'sdd12',S11")
        self._writeSCPI("CALC1:PAR:SEL 'sdd12'")
        self._writeSCPI("CALC1:FSIM:BAL:PAR:STAT ON")
        self._writeSCPI("CALC1:FSIM:BAL:PAR:BBAL:DEF SDD12")
        self._writeSCPI("DISP:WIND1:TRAC2:FEED 'sdd12'")

        # Create a trace called "sdd21" and for that trace turn on the balanced
        # transformation and set the balanced transformation to BBAL SDD21.
        self._writeSCPI("CALC1:PAR:DEF 'sdd21',S11")
        self._writeSCPI("CALC1:PAR:SEL 'sdd21'")
        self._writeSCPI("CALC1:FSIM:BAL:PAR:STAT ON")
        self._writeSCPI("CALC1:FSIM:BAL:PAR:BBAL:DEF SDD21")
        self._writeSCPI("DISP:WIND1:TRAC3:FEED 'sdd21'")

        # Now create reverse reflection parameters
        self._writeSCPI("CALC1:PAR:DEF 'sdd22',S11")
        self._writeSCPI("CALC1:PAR:SEL 'sdd22'")
        self._writeSCPI("CALC1:FSIM:BAL:PAR:STAT ON")
        self._writeSCPI("CALC1:FSIM:BAL:PAR:BBAL:DEF SDD22")
        self._writeSCPI("DISP:WIND1:TRAC4:FEED 'sdd22'")

        self._writeSCPI("TRIG:SOUR IMMediate")

    def captureS4PTrace(self, dtype=float):

        # Trigger trace and wait.
        isRunning = True
        while isRunning:
            msg = self._querySCPI("SENS1:SWEE:MODE SINGle;*OPC?")
            isRunning = (int(msg) == 0)
            time.sleep(0.01)

        s4Dict = dict(sdd11=None, sdd12=None, sdd21=None, sdd22=None)
        dtypeName = "RDATA" if dtype == complex else "FDATA"
        dataQuery = str.format("CALC1:DATA? {:s}", dtypeName)
        for s4Name in s4Dict.keys():
            cmd = str.format("CALC1:PAR:SEL '{:s}'", s4Name)
            self._writeSCPI(cmd)
            s4Dict[s4Name] = self.resource.query_ascii_values(dataQuery, container=np.array).squeeze()

        # Combine into 2x2xNUM_POINTS tensor
        s4Data = np.zeros((2, 2, s4Dict['sdd11'].size))
        s4Data[0, 0] = s4Dict['sdd11']
        s4Data[0, 1] = s4Dict['sdd12']
        s4Data[1, 0] = s4Dict['sdd21']
        s4Data[1, 1] = s4Dict['sdd22']
        return s4Data

    def setupECalibration(self, channel, startFreq, stopFreq, numPoints, sweepType):

        self.setupSweep(channel, startFreq, stopFreq, numPoints, sweepType)

        cmd = "sens1:corr:coll:guid:conn:port"
        fport = "2.92 mm female"
        mport = "2.92 mm male"
        self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, 1, fport))
        self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, 2, mport))
        self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, 3, fport))
        self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, 4, mport))

        cmd = "sens1:corr:coll:guid:ckit:port"
        kit = "N4692-60001 ECal 13226"
        self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, 1, kit))
        self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, 2, kit))
        self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, 3, kit))
        self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, 4, kit))

        self._writeSCPI("sens1:corr:pref:ecal:ori ON")
        self._writeSCPI("sens1:corr:coll:guid:thru:ports 1,2,1,4,2,3")
        self._writeSCPI("sens1:corr:coll:guid:init")

    def getNumberECalibrationSteps(self):
        return int(self._querySCPI("sens1:corr:coll:guid:steps?"))

    def getECalibrationStepDescription(self, step):
        return self._querySCPI(str.format("sens1:corr:coll:guid:desc? {:d}", step+1))

    def performECalibrationStep(self, step, save=True):
        if step >= self.getNumberECalibrationSteps():
            return
        self._writeSCPI(str.format("sens1:corr:coll:guid:acq STAN{:d}", step+1))
        time.sleep(2)
        if step == (self.getNumberECalibrationSteps()-1):
            self._writeSCPI("sens1:corr:coll:guid:save")

    def performECalibrationSteps(self):
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
    del vna
    #vna.query()
    #vna.setupSweep(10000000, 100000000, 100)

    print("Finished")
