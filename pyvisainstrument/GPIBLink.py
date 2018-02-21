"""GPIBLinkResource is a base class for various GPIB-based instruments
to control via SCPI.
"""
from __future__ import print_function
import time
import os
import visa

class GPIBLinkResource(object):
    """GPIBLinkResource is a base class for various GPIB-based instruments.
    Attributes:
        None
    """
    def __init__(self, busAddress, delay=35E-3):
        self.busAddress = busAddress
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
            raise Exception("GPIBLinkResource not open")
        time.sleep(self.delay)
        self.resource.write(cmd)

    def query(self, cmd, maxAttempts=3):
        """Perform raw SCPI query with retries
        Args:
            cmd (str): SCPI query
            maxAttempts (int): Number of attempts
        Returns:
            str: Query result
        """
        if not self.isOpen:
            raise Exception("GPIBLinkResource not open")
        err = Exception('Failed to perform query')
        for attempts in range(maxAttempts):
            try:
                rst = self.resource.query(cmd, delay=self.delay)
                return rst
            # pylint: disable=broad-except
            except Exception as curErr:
                print(str.format('Query attempt {:d} failed.', attempts))
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
            raise Exception("GPIBLinkResource not open")
        return self.resource.read(delay=self.delay)

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
        print(asrlInstrs)
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
                instID = inst.query("*IDN?", delay=100e-3)
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
