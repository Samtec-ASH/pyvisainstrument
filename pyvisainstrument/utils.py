"""Various helper routines."""
import os
import sys
import re
import socket
import subprocess
from subprocess import CalledProcessError
import pyvisa as visa
import zeroconf
from zeroconf import Zeroconf


def resolve_visa_address(addr: str, read_term=None, write_term=None, baud_rate=None) -> str:
    """ Helper function to resolve various VISA style addresses which isnt always trivial.
        HANDLERS:
            [ASRL::AUTO::<*IDN_MATCH>::INSTR]
                Resolve serial device w/ matching IDN field.
                COM ports can typically jump around.
            [<*AVAHI_SERVICE>._ssh._tcp.local]
            [<*AVAHI_SERVICE>._http._tcp.local]
                Resolve avahi services if given full service name (i.e. not just <*AVAHI_SERVICE>.local)
            [<*AVAHI_SERVICE>._smb._tcp.local]
                Resolve fake SAMBA avahi service w/ service prefix _smb
    Args:
        addr(str): Full visa resource address
        read_term(str, optional): Read termination (needed when query is required)
        write_term(str, optional): Write termination (needed when query is required)
        baud_rate(str|int, optional): Baud rate (needed when query is required)
    Returns:
        str: Resolved visa address
    """
    visa_addr = addr
    # Automatically determine ASRL resource address. ASRL::AUTO::<*IDN_MATCH>::INSTR
    if addr.startswith('ASRL::AUTO') and len(addr.split('::')) == 4:
        device_id = addr.split('::')[2]
        visa_addr = get_serial_bus_address(device_id, baud_rate, read_term, write_term)
        return visa_addr

    # Resolve avahi service to ipv4
    reg_str = r'([ A-z0-9._-])+.(_ssh|_http)._tcp.local'
    if re.search(reg_str, addr):
        service_name = re.search(reg_str, addr).group(0)
        service_ip = resolve_zeroconf_ip(service_name)
        visa_addr = re.sub(reg_str, service_ip, addr)
        return visa_addr

    # Resolve samba service to ipv4
    # NOTE: We've created fake avahi service type w/ suffix '._smb._tcp.local'
    # We use samba client to resolve ip address (nmblookup on Linux and smbutil on MacOS)
    # Mostly for older Windows that dont advertise via mdns
    reg_str = r'([ A-z0-9._-])+._smb._tcp.local'
    if re.search(reg_str, addr):
        service_name = re.search(reg_str, addr).group(0)
        service_name = service_name.replace('._smb._tcp.local', '')
        service_ip = resolve_samba_ip(service_name)
        visa_addr = re.sub(reg_str, service_ip, addr)
        return visa_addr

    return visa_addr


def resolve_zeroconf_ip(service_name: str) -> str:
    """ Resolve Zeroconf service IPv4 address.
    Args:
        service_name(str): Zeroconf service name
    Returns:
        str: IPv4 address
    """
    zc = Zeroconf()
    try:
        if not service_name.endswith('.'):
            service_name += '.'
        p = service_name.split('.')
        service_type = '.'.join(p[1:])
        info = zc.get_service_info(service_type, service_name)
        if info is None:
            raise Exception(f'Failed to resolve zeroconf service {service_name}')
        addresses = info.addresses_by_version(zeroconf.IPVersion.V4Only)
        if len(addresses) == 0:
            raise Exception(f'Failed to resolve zeroconf service to IPv4 address {service_name}')
        addr = socket.inet_ntoa(addresses[0])
        return addr
    except Exception as err:
        raise err
    finally:
        zc.close()


def resolve_samba_ip(hostname: str) -> str:
    """ Resolve SAMBA service IPv4 address.
    Args:
        service_name(str): SAMBA service name
    Returns:
        str: IPv4 address
    """

    try:
        address = None
        if sys.platform.startswith('linux'):
            rst = subprocess.check_output(['nmblookup', hostname])
            addresses = re.findall(r'[0-9]+(?:\.[0-9]+){3}', rst.decode())
            address = addresses[0] if len(addresses) > 0 else None
        if sys.platform == 'darwin':
            rst = subprocess.check_output(['smbutil', 'lookup', hostname])
            addresses = re.findall(r'[0-9]+(?:\.[0-9]+){3}', rst.decode())
            address = addresses[0] if len(addresses) > 0 else None
        if address is None:
            raise Exception(f'Failed to resolve SAMBA service {hostname}')
        return address
    except CalledProcessError as err:
        if err.returncode == 68:
            raise Exception(f'Failed to resolve SAMBA service {hostname}') from err
        raise err
    return hostname


def get_serial_bus_address(device_id, baud_rate=None, read_term=None, write_term=None):
    """ Convenience static method to auto-detect USB serial device by checking if
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


def is_binary_format(dformat: str) -> bool:
    ''' Check if data format is binary. '''
    return dformat.upper().startswith('REAL')


def is_ascii_format(dformat: str) -> bool:
    ''' Check if data format is ascii. '''
    return dformat.upper().startswith('ASC')


def get_binary_datatype(dformat: str) -> str:
    ''' Get datatype for binary data format. '''
    return 'd' if '64' in dformat else 'f'
