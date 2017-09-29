import visa
import time
import os

class GPIBLinkResource(object):
    """Base class for GPIB-based instruments."""
    def __init__(self, busAddress, delay=35E-3):
        self.busAddress = busAddress
        self.resource = None
        self.isOpen = False
        self.delay = delay
        self.ni_backend = os.getenv('NI_VISA_PATH', '@ni')

    def open(self):
        self.resource = visa.ResourceManager(self.ni_backend).open_resource(self.busAddress)
        self.resource.clear()
        self.resource.query_delay = self.delay
        self.isOpen = True

    def close(self):
        if self.resource:
            self.resource.write("*CLS")
            self.resource.write("*RST")
            self.resource.clear()
            self.resource.close()
        self.resource = None
        self.isOpen = False

    def write(self, cmd):
        if not self.isOpen:
            raise Exception("GPIBLinkResource not open")
        time.sleep(self.delay)
        self.resource.write(cmd)

    def query(self, cmd, maxAttempts=3):
        if not self.isOpen:
            raise Exception("GPIBLinkResource not open")
        err = None
        for attempts in range(maxAttempts):
            try:
                rst = self.resource.query(cmd, delay=self.delay)
                return rst
            except Exception as curErr:
                print(str.format('Query attempt {:d} failed.', attempts))
                err = curErr
        raise err

    def read(self):
        if not self.isOpen:
            raise Exception("GPIBLinkResource not open")
        return self.resource.read(delay=self.delay)

    @staticmethod
    def GetSerialBusAddress(deviceID, baudRate=None, readTerm=None, writeTerm=None):
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
            except Exception as err:
                if inst:
                    inst.clear()
                    inst.close()
                continue
        return None
