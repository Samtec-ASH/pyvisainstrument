"""AgilentVNA is a convience class to control various Agilent VNAs."""
from __future__ import print_function
import time
import numpy as np
from pyvisainstrument.VisaResource import VisaResource


# pylint: disable=too-many-public-methods
class AgilentVNA(VisaResource):
    """AgilentVNA is a convience class to control various Agilent VNAs."""
    def __init__(self, numPorts, *args, **kwargs):
        super(AgilentVNA, self).__init__(name='VNA', *args, **kwargs)
        self.numPorts = numPorts

    def setStartFreq(self, freq_hz, channel=1):
        """Set start frequency for channel.
        Args:
            freq_hz (float): Start freq in hertz
            channel (int): Channel number
        Returns:
            None
        """
        self.write('SENSE{:d}:FREQUENCY:START {:.0f}'.format(channel, freq_hz))

    def getStartFreq(self, channel=1):
        """Get start frequency for channel.
        Args:
            channel (int): Channel number
        Returns:
            float: Start freq in hertz
        """
        return self.query('SENSE{:d}:FREQUENCY:START?'.format(channel), container=float)

    def setStopFreq(self, freq_hz, channel=1):
        """Set stop frequency for channel.
        Args:
            freq_hz (float): Stop freq in hertz
            channel (int): Channel number
        Returns:
            None
        """
        self.write('SENSE{:d}:FREQUENCY:STOP {:.0f}'.format(channel, freq_hz))

    def getStopFreq(self, channel=1):
        """Get stop frequency for channel.
        Args:
            channel (int): Channel number
        Returns:
            float: Stop freq in hertz
        """
        return self.query('SENSE{:d}:FREQUENCY:STOP?'.format(channel), container=float)

    def setCenterFreq(self, freq_hz, channel=1):
        """Set center frequency for channel.
        Args:
            freq_hz (float): Center freq in hertz
            channel (int): Channel number
        Returns:
            None
        """
        self.write('SENSE{:d}:FREQUENCY:CENT {:.0f}'.format(channel, freq_hz))

    def getCenterFreq(self, channel=1):
        """Get center frequency for channel.
        Args:
            channel (int): Channel number
        Returns:
            float: Center freq in hertz
        """
        return self.query('SENSE{:d}:FREQUENCY:CENT?'.format(channel), container=float)

    def setCWFreq(self, freq_hz, channel=1):
        """Set CW frequency for channel.
        Args:
            freq_hz (float): CW freq in hertz
            channel (int): Channel number
        Returns:
            None
        """
        self.write('SENSE{:d}:FREQUENCY:CW {:.0f}'.format(channel, freq_hz))

    def getCWFreq(self, channel=1):
        """Get CW frequency for channel.
        Args:
            channel (int): Channel number
        Returns:
            float: CW freq in hertz
        """
        return self.query('SENSE{:d}:FREQUENCY:CW?'.format(channel), container=float)

    def setNumberSweepPoints(self, numPoints, channel=1):
        """Set number sweep points for channel.
        Args:
            numPoints (int): Number sweep points
            channel (int): Channel number
        Returns:
            None
        """
        self.write('SENSE{:d}:SWEEP:POINTS {:d}'.format(channel, numPoints))

    def getNumberSweepPoints(self, channel=1):
        """Get number sweep points for channel.
        Args:
            channel (int): Channel number
        Returns:
            int: Number sweep points
        """
        return self.query('SENSE{:d}:SWEEP:POINTS?'.format(channel), container=int)

    def setFrequencyStepSize(self, freq_hz, channel=1):
        """Set freq step size for channel.
        Args:
            freq_hz (float): Frequency step size in hertz
            channel (int): Channel number
        Returns:
            None
        """
        self.write('SENSE{0}:SWEEP:STEP {1:0.}'.format(channel, freq_hz))

    def getFrequencyStepSize(self, channel=1):
        """Get frequency step size
        Args:
            channel (int): Channel number
        Returns:
            float: Frequency step size in hertz
        """
        return self.query('SENSE{:d}:SWEEP:STEP?'.format(channel), container=float)

    def setSweepType(self, sweepType, channel=1):
        """Set sweep type.
        Args:
            sweepType (string): 'LINear | LOGarithmic | POWer | CW
                                 | SEGMent | PHASe'
            channel (int): Channel number
        Returns:
            None
        """
        self.write('SENSE{:d}:SWEEP:TYPE {:s}'.format(channel, sweepType))

    def getSweepType(self, channel=1):
        """Get sweep type.
        Args:
            channel (int): Channel number
        Returns:
            str: Sweep type
        """
        return self.query('SENSE{:d}:SWEEP:TYPE?'.format(channel))

    def setBandwidth(self, bwid, channel=1):
        """Set IF bandwidth.
        Args:
            bwid (int|string): Bandwidth in hertz ('MIN', 'MAX')
            channel (int): Channel number
        Returns:
            None
        """
        self.write('SENSE{0:d}:BWID {1}'.format(channel, bwid))

    def getBandwidth(self, channel=1):
        """Get IF bandwidth.
        Args:
            channel (int): Channel number
        Returns:
            int: Bandwidth in hertz
        """
        return self.query('SENSE{0:d}:BWID?'.format(channel), container=int)

    def setSweepMode(self, mode, channel=1):
        """Set sweep mode.
        Args:
            mode (str): One of HOLD | CONTinuous | GROups | SINGle
            channel (int): Channel number
        Returns:
            None
        """
        self.write('SENSE{:d}:SWEEP:MODE {:s}'.format(channel, mode))

    def getSweepMode(self, channel=1):
        """Get sweep mode.
        Args:
            channel (int): Channel number
        Returns:
            str: Sweep mode
        """
        return self.query('SENSE{:d}:SWEEP:MODE?'.format(channel))

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
        cmd = 'SENSE{0}:CORR:INT {1}'.format(channel, 'ON' if interpolate else 'OFF')
        self.write(cmd)
        cmd = 'SENSE{0}:CORR:CSET:ACT \'{1}\',{2}'.format(
            channel, calSet, '1' if applyCalStimulus else '0'
        )
        self.write(cmd)

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

    def setupSES4PTraces(self, portPairs=None):
        """Obsolete: Use setupSESTraces instead."""
        return self.setupSESTraces(portPairs=portPairs)

    def setupSESTraces(self, portPairs=None):
        """Convience method to setup single-ended sweep traces.
        Should be called after setting sweep params and mode.
        Args:
            None
        Returns:
            [str]: List of trace names
        """
        # Delete all measurements
        self.write('CALC1:PAR:DEL:ALL')

        if portPairs and len(portPairs) != 2:
            raise ValueError('portPairs must have length 2')
        # Default to all NxN pairs
        if portPairs is None:
            portPairs = 2*[list(range(self.numPorts))]

        # Turn on windows
        for i, a in enumerate(portPairs[0]):
            self.write('DISP:WIND{0}:STATE ON'.format(i+1))

        # Create all single ended s-params w/ name ch1_s{i}{j}
        traceNames = []
        for i, a in enumerate(portPairs[0]):
            for j, b in enumerate(portPairs[1]):
                tName = 'CH1_S{0}{1}'.format(a+1, b+1)
                sName = 'S{0}{1}'.format(a+1, b+1)
                traceNames.append(tName)
                self.write('CALC1:PAR:DEF \'{0}\',{1}'.format(tName, sName))
                self.write('CALC1:PAR:SEL \'{0}\''.format(tName))
                self.write('DISP:WIND{0}:TRAC{1}:FEED \'{2}\''.format(i+1, j+1, tName))
        self.write('TRIG:SOUR IMMediate')
        return traceNames

    def captureSES4PTrace(self, dtype=float, traceNames=None, portPairs=None):
        """Obsolete: Use captureSESTrace instead."""
        return self.captureSESTrace(dtype=dtype, traceNames=traceNames, portPairs=portPairs)

    def captureSESTrace(self, dtype=float, traceNames=None, portPairs=None):
        """Convience method to capture single-ended sweep traces.
        Should be called after setupSESTraces().
        Args:
            dtype: Data format either float or complex
            traceNames: Name of traces to capture
        Returns:
            Numpy.array: Numpy tensor with shape NxT if traceNames
            else NxSxS otherwise.
            T- Number of supplied traces
            N- 4 for single ended mode on 4-port
            F- Number of sweep points
        """
        # Trigger trace and wait.
        self.writeAsync('SENSE1:SWEEP:MODE SINGLE', delay=0.1)
        numPoints = self.getNumberSweepPoints()
        dtypeName = 'SDATA' if dtype == complex else 'FDATA'
        dataQuery = 'CALC1:DATA? {:s}'.format(dtypeName)
        # Get only provided traces data as FxT Tensor
        if traceNames:
            sData = np.zeros((numPoints, len(traceNames)), dtype=dtype)
            for i, traceName in enumerate(traceNames):
                self.write('CALC1:PAR:SEL \'{0}\''.format(traceName))
                data = self.query(dataQuery, container=np.ndarray).squeeze()
                # Complex is returned as alternating real,imag,...
                if dtype == complex:
                    data = data[0::2] + 1j*data[1::2]
                sData[:, i] = data

        # Get all single-ended s-params
        else:
            # Default to all NxN pairs
            if portPairs is None:
                portPairs = 2*[list(range(self.numPorts))]
            sData = np.zeros((numPoints, len(portPairs[0]), len(portPairs[1])), dtype=dtype)
            for i, a in enumerate(portPairs[0]):
                for j, b in enumerate(portPairs[1]):
                    self.write('CALC1:PAR:SEL \'CH1_S{0}{1}\''.format(a+1, b+1))
                    data = self.query(dataQuery, container=np.ndarray).squeeze()
                    # Complex is returned as alternating real,imag,...
                    if dtype == complex:
                        data = data[0::2] + 1j*data[1::2]
                    sData[:, i, j] = data
        return sData

    def setupS4PTraces(self):
        """Convience method to setup differential sweep traces for all
        diff s-params. Should be called after setting sweep params and mode.
        Args:
            None
        Returns:
            None
        """
        numDiffPairs = self.numPorts//2

        # Delete all measurements
        self.write('CALC1:PAR:DEL:ALL')
        self.write('CALC1:FSIM:BAL:DEV BBALANCED')
        self.write('CALC1:PAR:DEL:ALL')

        # Turn on N windows
        for i in range(numDiffPairs*numDiffPairs):
            self.write(str.format("DISP:WIND{0}:STATE ON", i+1))

        for i in range(numDiffPairs):
            for j in range(numDiffPairs):
                self.write('CALC1:PAR:DEF \'sdd{0}{1}\',S{0}{1}'.format(i+1, j+1))
                self.write('CALC1:PAR:SEL \'sdd{0}{1}\''.format(i+1, j+1))
                self.write('CALC1:FSIM:BAL:PAR:STATE ON')
                self.write('CALC1:FSIM:BAL:PAR:BBAL:DEF \'SDD{0}{1}\''.format(i+1, j+1))
                self.write('DISP:WIND{0}:TRAC{0}:FEED \'sdd{1}{2}\''.format(2*i+j+1, i+1, j+1))

        self.write('CALC1:FSIM:BAL:DEV BBALANCED')
        portList = ','.join([str(p+1) for p in range(self.numPorts)])
        self.write('CALC1:FSIM:BAL:TOP:BBAL:PPORTS {0}'.format(portList))
        self.write('TRIG:SOUR IMMEDIATE')

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
        numDiffPairs = self.numPorts//2
        # Trigger trace and wait.
        self.writeAsync('SENSE1:SWEEP:MODE SINGLE', delay=0.1)
        numPoints = self.getNumberSweepPoints()
        s4pData = np.zeros((numPoints, 2, 2), dtype=dtype)

        dtypeName = 'SDATA' if dtype == complex else 'FDATA'
        dataQuery = 'CALC1:DATA? {:s}'.format(dtypeName)
        for i in range(numDiffPairs):
            for j in range(numDiffPairs):
                self.write('CALC1:PAR:SEL \'sdd{0}{1}\''.format(i+1, j+1))
                data = self.query(dataQuery, container=np.ndarray).squeeze()
                # Complex is returned as alternating real,imag,...
                if dtype == complex:
                    data = data[0::2] + 1j*data[1::2]
                s4pData[:, i, j] = data
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
        cmd = 'SENSE1:CORR:COLL:GUID:CONN:PORT'
        for i, connector in enumerate(portConnectors):
            self.write('{:s}{:d} "{:s}"'.format(cmd, i+1, connector))

        # Set port e-cal kit (i.e. N4692-60003 ECal 13226)
        cmd = 'SENSE1:CORR:COLL:GUID:CKIT:PORT'
        for i, kit in enumerate(portKits):
            self.write('{:s}{:d} "{:s}"'.format(cmd, i+1, kit))

        # Set auto orientation setting
        self.write('SENSE1:CORR:PREF:ECAL:ORI {:s}'.format('ON' if autoOrient else 'OFF'))

        # Set port thru pairs or use default of VNA
        self.write('SENSE1:CORR:COLL:GUID:INIT')
        if portThruPairs:
            thruPairDef = ','.join([str(thru) for thru in portThruPairs])
            self.write('SENSE1:CORR:COLL:GUID:THRU:PORTS {:s}'.format(thruPairDef))
            self.write('SENSE1:CORR:COLL:GUID:INIT')

    def getNumberECalSteps(self):
        """Get total number e-cal steps to be performed.
        Must be called after setupECalibration().
        Args:
            None
        Returns:
            int: Number of e-cal steps
        """
        return self.query('SENSE1:CORR:COLL:GUID:STEPS?', container=int)

    def getECalStepInfo(self, step):
        """Get e-cal step description.
        Must be called after setupECalibration().
        Args:
            step (int): Index of e-cal step
        Returns:
            str: Description of e-cal step.
        """
        return self.query('SENSE1:CORR:COLL:GUID:DESC? {:d}'.format(step+1))

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
        self.writeAsync('SENSE1:CORR:COLL:GUID:ACQ STAN{:d},ASYN'.format(step+1), delay=0.4)
        time.sleep(delay)
        if step == (self.getNumberECalSteps()-1) and save:
            saveSuffix = 'SAVE:CSET "{:s}"'.format(saveName) if saveName else 'SAVE'
            self.write('SENSE1:CORR:COLL:GUID:{:s}'.format(saveSuffix))

    def performECalSteps(self, save=True, saveName=None, delay=5):
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
    print('Started')
    vna = AgilentVNA(busAddress="TCPIP::127.0.0.1::5020::SOCKET", numPorts=4)
    vna.open(writeTerm='\n', readTerm='\n')
    print(vna.getID())
    vna.setupSweep(1, 20E6, 30E6, 10, "LINEAR")
    vna.setupS4PTraces()
    print(vna.captureS4PTrace())
    vna.close()
    print('Finished')
