"""VisaResource is a base class for various VISA-style instruments."""
import logging
import time
import os
import visa
import numpy as np
logger = logging.getLogger('VISA')

class VisaResource:
    """VisaResource is a base class for various VISA-style instruments."""
    def __init__(self, name, busAddress, verbose=False, delay=35E-3):
        self.name = name
        self.busAddress = busAddress
        self.verbose = verbose
        self.resource = None
        self.isOpen = False
        self.delay = delay
        self.ni_backend = os.getenv('NI_VISA_PATH', '@ni')

    def open(self, readTerm=None, writeTerm=None, baudRate=None):
        """Open instrument connection.
        Args:
            baudRate (int, optional): Baud rate in hertz
            readTerm (str, optional): Read termination chars
            writeTerm (str, optional): Write termination chars
        Returns:
            None
        """
        self.resource = visa.ResourceManager(self.ni_backend).open_resource(self.busAddress)
        # self.resource.clear()
        self.resource.query_delay = self.delay
        if readTerm:
            self.resource.read_termination = readTerm
        if writeTerm:
            self.resource.write_termination = writeTerm
        if baudRate:
            self.resource.baud_rate = baudRate
        self.isOpen = True

    def close(self):
        """Clear and close instrument connection.
        Args:
            None
        Returns:
            None
        """
        if self.resource:
            self.resource.write("*CLS")
            time.sleep(self.delay)
            # self.resource.clear()
            self.resource.close()
        self.resource = None
        self.isOpen = False

    def write(self, cmd):
        """Perform raw SCPI write
        Args:
            cmd (str): SCPI command
        Returns:
            None
        """
        if not self.isOpen:
            raise Exception("VisaResource not open")
        time.sleep(self.delay)
        logger.debug('%s:WRITE %s', self.name, cmd)
        self.resource.write(cmd)

    def writeAsync(self, cmd, delay=0.1):
        """Perform SCPI command asynchronously for long running commands.
        Note: This still blocks current thread just not device.
        Args:
            cmd (str): SCPI command
        Returns:
            rst: Numpy array
        """
        self.write('*CLS')
        self.write(cmd)
        self.write('*OPC')
        isComplete = False
        while not isComplete:
            msg = self.query('*ESR?')
            isComplete = (int(msg) & 0x01)
            if not isComplete:
                time.sleep(delay)

    def query(self, cmd, container=str, maxAttempts=3):
        """Perform raw SCPI query with retries
        Args:
            cmd (str): SCPI query
            container: str, float, bool, np.array
            maxAttempts (int): Number of attempts
        Returns:
            str: Query result
        """
        if not self.isOpen:
            raise Exception("VisaResource not open")
        err = Exception('Failed to perform query')
        for attempts in range(maxAttempts):
            try:
                # Special case for arrays
                if container in [np.ndarray, np.array, list]:
                    rst = self.resource.query_ascii_values(cmd, container=container)
                    if self.verbose:
                        logger.debug('%s:QUERY %s -> Array', self.name, cmd)
                else:
                    rst = self.resource.query(cmd, delay=self.delay)
                    if self.verbose:
                        logger.debug('%s:QUERY %s -> %s', self.name, cmd, rst)
                    if container is bool:
                        rst = rst.lower() not in ['0', 'false', 'no']
                    else:
                        rst = container(rst)
                return rst
            # pylint: disable=broad-except
            except Exception as curErr:
                logger.warning('Query attempt %d of %d failed.', attempts+1, maxAttempts)
                err = curErr
        raise err

    def read(self):
        """Perform raw SCPI read
        Args:
            None
        Returns:
            str: Read result
        """
        if not self.isOpen:
            # pylint: disable=broad-except
            raise Exception("VisaResource not open")
        rst = self.resource.read(delay=self.delay)
        if self.verbose:
            logger.debug('%s:READ %s', self.name, rst)

    def getID(self):
        """Get identifier.
        Args:
            None
        Returns:
            str: ID
        """
        return self.query('*IDN?')

    @staticmethod
    def GetSerialBusAddress(deviceID, baudRate=None, readTerm=None, writeTerm=None):
        """Convience static method to auto-detect USB serial device by checking if
        provided deviceID is in *IDN result.
        Args:
            deviceID (str): Device ID to search for
            baudRate (int, optional): Baud rate in hertz
            readTerm (str, optional): Read termination chars
            writeTerm (str, optional): Write termination chars
        Returns:
            str: Read result
        """
        ni_backend = os.getenv('NI_VISA_PATH', '@ni')
        asrlInstrs = visa.ResourceManager(ni_backend).list_resources('ASRL?*::INSTR')
        for addr in asrlInstrs:
            inst = None
            try:
                inst = visa.ResourceManager(ni_backend).open_resource(addr, open_timeout=2)
                if baudRate:
                    inst.baud_rate = baudRate
                if readTerm:
                    inst.read_termination = readTerm
                if writeTerm:
                    inst.write_termination = writeTerm
                inst.timeout = 2000
                instID = inst.query('*IDN?', delay=100e-3)
                inst.clear()
                inst.close()
                if deviceID in instID:
                    return addr
            # pylint: disable=broad-except
            except Exception:
                if inst:
                    inst.clear()
                    inst.close()
                continue
        return None
