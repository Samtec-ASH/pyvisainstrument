import visa
import time


class GPIBLinkResource(object):
    """Base class for GPIB-based instruments."""
    def __init__(self, busAddress, delay=15E-3):
        self.busAddress = busAddress
        self.resource = None
        self.isOpen = False
        self.delay = delay

    def open(self):
        self.resource = visa.ResourceManager().open_resource(self.busAddress)
        self.isOpen = True

    def close(self):
        self.resource.close()
        self.resource = None
        self.isOpen = False

    def write(self, cmd):
        if not self.isOpen:
            raise Exception("GPIBLinkResource not open")
        time.sleep(self.delay)
        self.resource.write(cmd)

    def query(self, cmd):
        if not self.isOpen:
            raise Exception("GPIBLinkResource not open")
        return self.resource.query(cmd, delay=self.delay)

    def read(self):
        if not self.isOpen:
            raise Exception("GPIBLinkResource not open")
        return self.resource.read(delay=self.delay)
