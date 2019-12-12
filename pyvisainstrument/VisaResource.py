"""VisaResource is a base class for various VISA-style instruments."""
import logging
import time
import os
import visa
import numpy as np
logger = logging.getLogger('VISA')


class VisaResource:
    """VisaResource is a base class for various VISA-style instruments."""

    def __init__(self, name, bus_address, verbose=False, delay=35E-3):
        self.name = name
        self.bus_address = bus_address
        self.verbose = verbose
        self.resource = None
        self.is_open = False
        self.delay = delay
        self.ni_backend = os.getenv('NI_VISA_PATH', '@ni')

    def open(self, read_term=None, write_term=None, baud_rate=None):
        """Open instrument connection.
        Args:
            baud_rate (int, optional): Baud rate in hertz
            read_term (str, optional): Read termination chars
            write_term (str, optional): Write termination chars
        Returns:
            None
        """
        bus_address = self.bus_address
        # Automatically determine ASRL resource address. ASRL::AUTO::<*IDN_MATCH>::INSTR
        if bus_address.startswith('ASRL::AUTO') and len(bus_address.split('::')) == 4:
            device_id = bus_address.split('::')[2]
            bus_address = VisaResource.GetSerialBusAddress(device_id, baud_rate, read_term, write_term)
        self.resource = visa.ResourceManager(self.ni_backend).open_resource(bus_address)
        # self.resource.clear()
        self.resource.query_delay = self.delay
        if read_term:
            self.resource.read_termination = read_term
        if write_term:
            self.resource.write_termination = write_term
        if baud_rate:
            self.resource.baud_rate = baud_rate
        self.is_open = True

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
        self.is_open = False

    def write(self, cmd):
        """Perform raw SCPI write
        Args:
            cmd (str): SCPI command
        Returns:
            None
        """
        if not self.is_open:
            raise Exception("VisaResource not open")
        time.sleep(self.delay)
        logger.debug('%s:WRITE %s', self.name, cmd)
        self.resource.write(cmd)

    def write_async(self, cmd, delay=0.1):
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
        complete = False
        while not complete:
            msg = self.query('*ESR?')
            complete = (int(msg) & 0x01)
            if not complete:
                time.sleep(delay)

    def query(self, cmd, container=str, max_attempts=3, dformat='ASCii,0',
              big_endian=True, chunk_size=None):
        """Perform raw SCPI query with retries
        Args:
            cmd (str): SCPI query
            container: str, float, bool, np.array
            max_attempts (int): Number of attempts
        Returns:
            str: Query result
        """
        if not self.is_open:
            raise Exception("VisaResource not open")
        err = Exception('Failed to perform query')
        for attempts in range(max_attempts):
            try:
                # Special case for arrays
                if container in [np.ndarray, np.array, list]:
                    if dformat.upper().startswith('REAL'):
                        datatype = 'd' if '64' in dformat else 'f'
                        rst = self.resource.query_binary_values(
                            cmd, is_big_endian=big_endian, datatype=datatype,
                            container=np.array, chunk_size=chunk_size
                        )
                    else:
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
                logger.warning(
                    'Query attempt %d of %d failed for <%s>.',
                    attempts + 1, max_attempts, cmd
                )
                err = curErr
        raise err

    def read(self):
        """Perform raw SCPI read
        Args:
            None
        Returns:
            str: Read result
        """
        if not self.is_open:
            # pylint: disable=broad-except
            raise Exception("VisaResource not open")
        rst = self.resource.read(delay=self.delay)
        if self.verbose:
            logger.debug('%s:READ %s', self.name, rst)

    def get_id(self):
        """Get identifier.
        Args:
            None
        Returns:
            str: ID
        """
        return self.query('*IDN?')

    @staticmethod
    def GetSerialBusAddress(device_id, baud_rate=None, read_term=None, write_term=None):
        """Convenience static method to auto-detect USB serial device by checking if
        provided device_id is in *IDN result.
        Args:
            device_id (str): Device ID to search for
            baud_rate (int, optional): Baud rate in hertz
            read_term (str, optional): Read termination chars
            write_term (str, optional): Write termination chars
        Returns:
            str: Read result
        """
        rmi = visa.ResourceManager(os.getenv('NI_VISA_PATH', '@ni'))
        used_resource_names = []  # [r.resource_name for r in rmi.list_opened_resources()]
        avail_resource_names = rmi.list_resources('ASRL?*::INSTR')
        filt_resource_names = list(filter(
            lambda x: x not in used_resource_names, avail_resource_names
        ))
        target_resource_name = None
        for resource_name in filt_resource_names:
            resource = None
            try:
                resource = rmi.open_resource(resource_name, open_timeout=0.3)
                if baud_rate:
                    resource.baud_rate = baud_rate
                if read_term:
                    resource.read_termination = read_term
                if write_term:
                    resource.write_termination = write_term
                resource.timeout = 500
                resource_id = resource.query('*IDN?', delay=0.3)
                resource.clear()
                resource.close()
                if device_id in resource_id:
                    target_resource_name = resource_name
                    break
            # pylint: disable=broad-except
            except Exception:
                try:
                    if resource:
                        resource.clear()
                        resource.close()
                except Exception:
                    pass
                continue
        if target_resource_name:
            return target_resource_name
        raise Exception((
            f'Unable to find serial device w/ ID: {device_id}. '
            f'Please verify device is powered, connected, and not already in use. '
            f'Available devices: {filt_resource_names}. '
        ))
