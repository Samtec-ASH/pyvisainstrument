
"""AgilentVNA is a convience class to control various Agilent VNAs via SCPI
"""

from __future__ import print_function
import time
import numpy as np
from pyvisainstrument.GPIBLink import GPIBLinkResource

# pylint: disable=too-many-public-methods
class AgilentVNA(GPIBLinkResource):
    """AgilentVNA is a convience class to control various Agilent
    VNAs via SCPI.
    Atributes:
        None
    """
    def __init__(self, busLinkAddress, verbose=False):
        """Init function."""
        super(AgilentVNA, self).__init__(busAddress=busLinkAddress)
        self.verbose = verbose
        self.busLinkAddress = busLinkAddress

    # pylint: disable=arguments-differ,useless-super-delegation
    def open(self, *args, **kwargs):
        """Open instrument connection.
        Args:
            None
        Returns:
            None
        """
        super(AgilentVNA, self).open(*args, **kwargs)

    # pylint: disable=arguments-differ,useless-super-delegation
    def close(self):
        """Close instrument connection.
        Args:
            None
        Returns:
            None
        """
        super(AgilentVNA, self).close()

    def getID(self):
        """Get identifier.
        Args:
            None
        Returns:
            str: ID
        """
        return str(self._querySCPI("*IDN?"))

    def _writeSCPI(self, scpiStr):
        """Perform raw SCPI write
        Args:
            scpiStr (str): SCPI command
        Returns:
            None
        """
        if self.verbose:
            print(str.format("VNA.write({:s})", scpiStr))
        self.write(scpiStr)

    def _querySCPI(self, scpiStr):
        """Perform raw SCPI query
        Args:
            scpiStr (str): SCPI query
        Returns:
            str: Query result
        """
        rst = self.query(scpiStr)
        if self.verbose:
            print(str.format("VNA.query({:s}) -> {:s}", scpiStr, rst))
        return rst

    def _queryAsciiValues(self, scpiStr):
        """Perform SCPI query of ascii-based values
        Args:
            scpiStr (str): SCPI query
        Returns:
            rst: Numpy array
        """
        rst = self.resource.query_ascii_values(scpiStr, container=np.array)
        if self.verbose:
            print('VNA.query({0})'.format(scpiStr))
        return rst

    def _writeAsyncSCPI(self, scpiStr, delay=0.1):
        """Perform SCPI query asynchronously for long running commands
        Args:
            scpiStr (str): SCPI query
        Returns:
            rst: Numpy array
        """
        self._writeSCPI('*CLS')
        self._writeSCPI(scpiStr)
        self._writeSCPI('*OPC')
        isComplete = False
        while not isComplete:
            msg = self._querySCPI("*ESR?")
            isComplete = (int(msg) & 0x01)
            if not isComplete:
                time.sleep(delay)

    def setStartFreq(self, freq_hz, channel=1):
        """Set start frequency for channel.
        Args:
            freq_hz (float): Start freq in hertz
            channel (int): Channel number
        Returns:
            None
        """
        cmd = str.format("SENSE{:d}:FREQUENCY:START {:.0f}", channel, freq_hz)
        self._writeSCPI(cmd)

    def getStartFreq(self, channel=1):
        """Get start frequency for channel.
        Args:
            channel (int): Channel number
        Returns:
            float: Start freq in hertz
        """
        cmd = str.format("SENSE{:d}:FREQUENCY:START?", channel)
        rst = float(self._querySCPI(cmd))
        return rst

    def setStopFreq(self, freq_hz, channel=1):
        """Set stop frequency for channel.
        Args:
            freq_hz (float): Stop freq in hertz
            channel (int): Channel number
        Returns:
            None
        """
        cmd = str.format("SENSE{:d}:FREQUENCY:STOP {:.0f}", channel, freq_hz)
        self._writeSCPI(cmd)

    def getStopFreq(self, channel=1):
        """Get stop frequency for channel.
        Args:
            channel (int): Channel number
        Returns:
            float: Stop freq in hertz
        """
        cmd = str.format("SENSE{:d}:FREQUENCY:STOP?", channel)
        rst = float(self._querySCPI(cmd))
        return rst

    def setCenterFreq(self, freq_hz, channel=1):
        """Set center frequency for channel.
        Args:
            freq_hz (float): Center freq in hertz
            channel (int): Channel number
        Returns:
            None
        """
        cmd = str.format("SENSE{:d}:FREQUENCY:CENT {:.0f}", channel, freq_hz)
        self._writeSCPI(cmd)

    def getCenterFreq(self, channel=1):
        """Get center frequency for channel.
        Args:
            channel (int): Channel number
        Returns:
            float: Center freq in hertz
        """
        cmd = str.format("SENSE{:d}:FREQUENCY:CENT?", channel)
        rst = float(self._querySCPI(cmd))
        return rst

    def setCWFreq(self, freq_hz, channel=1):
        """Set CW frequency for channel.
        Args:
            freq_hz (float): CW freq in hertz
            channel (int): Channel number
        Returns:
            None
        """
        cmd = str.format("SENSE{:d}:FREQUENCY:CW {:.0f}", channel, freq_hz)
        self._writeSCPI(cmd)

    def getCWFreq(self, channel=1):
        """Get CW frequency for channel.
        Args:
            channel (int): Channel number
        Returns:
            float: CW freq in hertz
        """
        cmd = str.format("SENSE{:d}:FREQUENCY:CW?", channel)
        rst = float(self._querySCPI(cmd))
        return rst

    def setNumberSweepPoints(self, numPoints, channel=1):
        """Set number sweep points for channel.
        Args:
            numPoints (int): Number sweep points
            channel (int): Channel number
        Returns:
            None
        """
        cmd = str.format("SENSE{:d}:SWEEP:POINTS {:d}", channel, numPoints)
        self._writeSCPI(cmd)

    def getNumberSweepPoints(self, channel=1):
        """Get number sweep points for channel.
        Args:
            channel (int): Channel number
        Returns:
            int: Number sweep points
        """
        cmd = str.format("SENSE{:d}:SWEEP:POINTS?", channel)
        rst = int(self._querySCPI(cmd))
        return rst

    def setFrequencyStepSize(self, freq_hz, channel=1):
        """Set freq step size for channel.
        Args:
            freq_hz (float): Frequency step size in hertz
            channel (int): Channel number
        Returns:
            None
        """
        cmd = str.format("SENSE{:d}:SWEEP:STEP {1:0.}", channel, freq_hz)
        self._writeSCPI(cmd)

    def getFrequencyStepSize(self, channel=1):
        """Get frequency step size
        Args:
            channel (int): Channel number
        Returns:
            float: Frequency step size in hertz
        """
        cmd = str.format("SENSE{:d}:SWEEP:STEP?", channel)
        rst = float(self._querySCPI(cmd))
        return rst

    def setSweepType(self, sweepType, channel=1):
        """Set sweep type.
        Args:
            sweepType (string): 'LINear | LOGarithmic | POWer | CW
                                 | SEGMent | PHASe'
            channel (int): Channel number
        Returns:
            None
        """
        cmd = str.format("SENSE{:d}:SWEEP:TYPE {:s}", channel, sweepType)
        self._writeSCPI(cmd)

    def getSweepType(self, channel=1):
        """Get sweep type.
        Args:
            channel (int): Channel number
        Returns:
            str: Sweep type
        """
        cmd = str.format("SENSE{:d}:SWEEP:TYPE?", channel)
        rst = str(self._querySCPI(cmd))
        return rst

    def setBandwidth(self, bwid, channel=1):
        """Set IF bandwidth.
        Args:
            bwid (int|string): Bandwidth in hertz ('MIN', 'MAX')
            channel (int): Channel number
        Returns:
            None
        """
        cmd = str.format("SENSE{0:d}:BWID {1}", channel, bwid)
        self._writeSCPI(cmd)

    def getBandwidth(self, channel=1):
        """Get IF bandwidth.
        Args:
            channel (int): Channel number
        Returns:
            int: Bandwidth in hertz
        """
        cmd = str.format("SENSE{0:d}:BWID?", channel)
        rst = int(self._querySCPI(cmd))
        return rst

    def setSweepMode(self, mode, channel=1):
        """Set sweep mode.
        Args:
            mode (str): One of HOLD | CONTinuous | GROups | SINGle
            channel (int): Channel number
        Returns:
            None
        """
        cmd = str.format("SENSE{:d}:SWEEP:MODE {:s}", channel, mode)
        self._writeSCPI(cmd)

    def getSweepMode(self, channel=1):
        """Get sweep mode.
        Args:
            channel (int): Channel number
        Returns:
            str: Sweep mode
        """
        cmd = str.format("SENSE{:d}:SWEEP:MODE?", channel)
        rst = int(self._querySCPI(cmd))
        return rst

    def setActiveCalSet(self, calSet, interpolate=True, applyCalStimulus=True, channel=1):
        """Select and applies cal set to specified channel
        Can get list of cal sets with SENS:CORR:CSET:CAT?
        Args:
            calSet (str): Cal Set to make active
            interpolate (bool): Interpolate data points
            channel (int): Channel number
        Returns:
            None
        """
        cmd = "SENSE:CORR:INT {:s}".format('ON' if interpolate else 'OFF')
        self._writeSCPI(cmd)
        cmd = str.format("SENSE{0}:CORR:CSET:ACT '{1}',{2}",
                         channel, calSet, '1' if applyCalStimulus else '0')
        self._writeSCPI(cmd)

    # pylint: disable=too-many-arguments
    def setupSweep(self, startFreq, stopFreq, numPoints, sweepType="LINEAR", channel=1):
        """Convience method to configure common sweep parameters
        Args:
            startFreq (float): Start frequency in Hz
            stopFreq (float): Stop frequency in Hz
            numPoints (int): Number frequency points
            sweepType (str): Sweep type [see setSweepType()]
            channel (int): Channel number
        Returns:
            None
        """
        self.setStartFreq(startFreq, channel=channel)
        self.setStopFreq(stopFreq, channel=channel)
        self.setNumberSweepPoints(numPoints, channel=channel)
        self.setSweepType(sweepType, channel=channel)

    def setupSES4PTraces(self):
        """Convience method to setup single-ended sweep traces for all
        16 s-params. Should be called after setting sweep params and mode.
        Args:
            None
        Returns:
            [str]: List of trace names
        """
        # Delete all measurements
        self._writeSCPI("CALC1:PAR:DEL:ALL")

        # Turn on 4 windows
        for i in range(1, 5):
            self._writeSCPI(str.format("DISP:WIND{0}:STATE ON", i))

        # Create all 16 single ended s-params w/ name ch1_s{i}{j}
        traceNames = []
        for i in range(1, 5):
            for j in range(1, 5):
                traceName = str.format("ch1_s{0}{1}", i, j)
                traceNames.append(traceName)
                self._writeSCPI(str.format("CALC1:PAR:DEF 'ch1_s{0}{1}',S{0}{1}", i, j))
                self._writeSCPI(str.format("CALC1:PAR:SEL 'ch1_s{0}{1}'", i, j))
                self._writeSCPI(str.format("DISP:WIND{0}:TRAC{1}:FEED 'ch1_s{0}{1}'", i, j))

        self._writeSCPI("TRIG:SOUR IMMediate")
        return traceNames

    def captureSES4PTrace(self, dtype=float, traceNames=None):
        """Convience method to capture single-ended sweep traces for all
        SE s-params or those provided as input.
        Should be called after setupSES4PTraces().
        Args:
            dtype: Data format either float or complex
            traceNames: Name of traces to capture
        Returns:
            Numpy.array: Numpy tensor with shape NxT if traceNames
            else NxSxS otherwise.
            T- Number of supplied traces
            S- 4 for single ended mode on 4-port
            N- Number of sweep points
        """
        # Trigger trace and wait.
        self._writeAsyncSCPI('SENSE1:SWEEP:MODE SINGLE', delay=0.1)
        numPoints = self.getNumberSweepPoints()
        dtypeName = "SDATA" if dtype == complex else "FDATA"
        dataQuery = str.format("CALC1:DATA? {:s}", dtypeName)

        # Get only provided traces data as NxT Tensor
        if traceNames:
            s4pData = np.zeros((numPoints, len(traceNames)), dtype=dtype)
            for i, traceName in enumerate(traceNames):
                cmd = str.format("CALC1:PAR:SEL '{0}'", traceName)
                self._writeSCPI(cmd)
                data = self._queryAsciiValues(dataQuery).squeeze()
                if dtype == complex:
                    data = data.view(dtype=complex)
                s4pData[:, i] = data

        # Get all 16 traces data as NxSxS Tensor
        else:
            s4pData = np.zeros((numPoints, 4, 4), dtype=dtype)
            for i in range(1, 5):
                for j in range(1, 5):
                    cmd = str.format("CALC1:PAR:SEL 'ch1_s{0}{1}'", i, j)
                    self._writeSCPI(cmd)
                    data = self._queryAsciiValues(dataQuery).squeeze()
                    # Complex is returned as alternating real,imag,...
                    if dtype == complex:
                        data = data.view(dtype=complex)
                    s4pData[:, i-1, j-1] = data
        return s4pData

    def setupS4PTraces(self):
        """Convience method to setup differential sweep traces for all
        diff s-params. Should be called after setting sweep params and mode.
        Args:
            None
        Returns:
            None
        """
        # Delete all measurements
        self._writeSCPI("CALC1:PAR:DEL:ALL")
        self._writeSCPI("CALC1:FSIM:BAL:DEV BBALANCED")
        self._writeSCPI("CALC1:PAR:DEL:ALL")

        # Turn on 4 windows
        for i in range(1, 5):
            self._writeSCPI(str.format("DISP:WIND{0}:STATE ON", i))

        for i in range(1, 3):
            for j in range(1, 3):
                self._writeSCPI("CALC1:PAR:DEF 'sdd{0}{1}',S{0}{1}".format(i, j))
                self._writeSCPI("CALC1:PAR:SEL 'sdd{0}{1}'".format(i, j))
                self._writeSCPI("CALC1:FSIM:BAL:PAR:STATE ON")
                self._writeSCPI("CALC1:FSIM:BAL:PAR:BBAL:DEF 'SDD{0}{1}'".format(i, j))
                self._writeSCPI("DISP:WIND{0}:TRAC{0}:FEED 'sdd{1}{2}'".format(2*(i-1)+j, i, j))

        self._writeSCPI("CALC1:FSIM:BAL:DEV BBALANCED")
        self._writeSCPI("CALC1:FSIM:BAL:TOP:BBAL:PPORTS 1,2,3,4")
        self._writeSCPI("TRIG:SOUR IMMEDIATE")

    def captureS4PTrace(self, dtype=float):
        """Convience method to capture differential sweep traces for
        all diff s-params SDD11, SDD12, SDD21, & SDD22.
        Should be called after setupS4PTraces().
        Args:
            dtype: Data format either float or complex
        Returns:
            Numpy.array: Numpy tensor with shape NxSxS
            S- 2 for differential mode on 4-port
            N- Number of sweep points
        """
        # Trigger trace and wait.
        self._writeAsyncSCPI('SENSE1:SWEEP:MODE SINGLE', delay=0.1)
        numPoints = self.getNumberSweepPoints()
        s4pData = np.zeros((numPoints, 2, 2), dtype=dtype)

        dtypeName = "SDATA" if dtype == complex else "FDATA"
        dataQuery = str.format("CALC1:DATA? {:s}", dtypeName)
        for i in range(1, 3):
            for j in range(1, 3):
                cmd = str.format("CALC1:PAR:SEL 'sdd{0}{1}'", i, j)
                self._writeSCPI(cmd)
                data = self._queryAsciiValues(dataQuery).squeeze()
                # Complex is returned as alternating real,imag,...
                if dtype == complex:
                    data = data.view(dtype=complex)
                s4pData[:, i-1, j-1] = data
        return s4pData

    def setupECalibration(self, portConnectors, portKits, portThruPairs=None, autoOrient=True):
        """Convience method to perform guided calibration w/ e-cal module
        Args:
            portConnectors ([str]):
                Defines connection for each port.
                Index corresponds to (port number-1).
                E.g. ['2.92 mm female', '2.92 mm female']
            portKits ([str]):
                Defines e-cal kit used for each port.
                Index corresponds to (port number-1).
                E.g. ['N4692-60003 ECal 13226', 'N4692-60003 ECal 13226']
            portThruPairs ([int], optional):
                Defines port pairs to perform cal on.
                Defaults to min required by VNA.
                E.g [1,2,1,3,1,4,2,3,2,4,3,4]
            autoOrient (bool, optional)
                To auto determine port connection orientation
                Default is True
        Returns:
            None
        """
        if not isinstance(portConnectors, list) or not isinstance(portKits, list):
            raise Exception('portConnectors and portKits must be of type list')

        if len(portConnectors) != len(portKits):
            raise Exception('portConnectors and portKits must have same length')

        if portThruPairs and not isinstance(portThruPairs, list) or len(portThruPairs) % 2:
            raise Exception('portThruPairs must be a list of even length')

        # Set port connector (i.e. 2.92 mm female)
        cmd = "SENSE1:CORR:COLL:GUID:CONN:PORT"
        for i, connector in enumerate(portConnectors):
            self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, i+1, connector))

        # Set port e-cal kit (i.e. N4692-60003 ECal 13226)
        cmd = "SENSE1:CORR:COLL:GUID:CKIT:PORT"
        for i, kit in enumerate(portKits):
            self._writeSCPI(str.format('{:s}{:d} "{:s}"', cmd, i+1, kit))

        # Set auto orientation setting
        cmd = str.format("SENSE1:CORR:PREF:ECAL:ORI {:s}", "ON" if autoOrient else "OFF")
        self._writeSCPI(cmd)

        # Set port thru pairs or use default of VNA
        self._writeSCPI("SENSE1:CORR:COLL:GUID:INIT")
        if portThruPairs:
            thruPairDef = ','.join([str(thru) for thru in portThruPairs])
            self._writeSCPI(str.format("SENSE1:CORR:COLL:GUID:THRU:PORTS {:s}", thruPairDef))
            self._writeSCPI("SENSE1:CORR:COLL:GUID:INIT")

    def getNumberECalSteps(self):
        """Get total number e-cal steps to be performed.
        Must be called after setupECalibration().
        Args:
            None
        Returns:
            int: Number of e-cal steps
        """
        return int(self._querySCPI("SENSE1:CORR:COLL:GUID:STEPS?"))

    def getECalStepInfo(self, step):
        """Get e-cal step description.
        Must be called after setupECalibration().
        Args:
            step (int): Index of e-cal step
        Returns:
            str: Description of e-cal step.
        """
        return self._querySCPI(str.format("SENSE1:CORR:COLL:GUID:DESC? {:d}", step+1))

    def performECalStep(self, step, save=True, saveName=None, delay=2):
        """Perform e-cal step. Should be done in order.
        Must be called after setupECalibration().
        Best used for asynchronous execution.
        For synchronous, use performECalSteps() iterator.
        Args:
            step (int): Index of e-cal step to perform.
            save (bool, optional): To save results if last step
        Returns:
            None
        """
        if step >= self.getNumberECalSteps():
            return
        self._writeSCPI("*CLS")
        self._writeSCPI(str.format("SENSE1:CORR:COLL:GUID:ACQ STAN{:d},ASYN", step+1))
        self._writeSCPI('*OPC')
        isComplete = False
        while not isComplete:
            msg = self._querySCPI("*ESR?")
            isComplete = (int(msg) & 0x01)
            time.sleep(0.4)
        time.sleep(delay)
        if step == (self.getNumberECalSteps()-1) and save:
            saveSuffix = 'SAVE:CSET "{:s}"'.format(saveName) if saveName else 'SAVE'
            self._writeSCPI('SENSE1:CORR:COLL:GUID:{:s}'.format(saveSuffix))

    def performECalSteps(self, save=True, saveName=None, delay=15):
        """Perform all e-cal steps as iterator.
        Must be called after setupECalibration().
        Best used for synchronous execution.
        >>> vna.setupECalibration(...)
        >>> for stepDescription in vna.performECalSteps():
        >>>     print(stepDescription)
        Args:
            None
        Yields:
            str: Description of next step
        Returns:
            None
        """
        numSteps = self.getNumberECalSteps()
        i = 0
        while i < numSteps:
            msg = self.getECalStepInfo(i)
            yield msg
            self.performECalStep(i, save=save, saveName=saveName, delay=delay)
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
