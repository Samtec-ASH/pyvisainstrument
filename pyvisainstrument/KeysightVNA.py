""" KeysightVNA enables controlling various Keysight VNA/PNAs. """
from __future__ import print_function
import time
from typing import Union, Optional, List, Tuple, Dict
import logging
import numpy as np
from .utils import is_binary_format, get_binary_datatype
from .VisaResource import VisaResource
logger = logging.getLogger('VISA')


class KeysightVNA(VisaResource):
    """ KeysightVNA enables controlling various Keysight VNA/PNAs. """

    def __init__(self, num_ports: int, *args, **kwargs):
        super().__init__(name='VNA', *args, **kwargs)
        self.num_ports = num_ports

    def set_start_freq(self, freq_hz: float, channel: int = 1):
        """ Set start frequency for channel.
        Args:
            freq_hz (float): Start freq in hertz
            channel (int): Channel number
        """
        self.write(f'SENSE{channel:d}:FREQUENCY:START {freq_hz:.0f}')

    def get_start_freq(self, channel: int = 1) -> float:
        """ Get start frequency for channel.
        Args:
            channel (int): Channel number
        Returns:
            float: Start freq in hertz
        """
        return self.query(f'SENSE{channel:d}:FREQUENCY:START?', container=float)

    def set_stop_freq(self, freq_hz: float, channel: int = 1):
        """ Set stop frequency for channel.
        Args:
            freq_hz (float): Stop freq in hertz
            channel (int): Channel number
        """
        self.write(f'SENSE{channel:d}:FREQUENCY:STOP {freq_hz:.0f}')

    def get_stop_freq(self, channel: int = 1) -> float:
        """ Get stop frequency for channel.
        Args:
            channel (int): Channel number
        Returns:
            float: Stop freq in hertz
        """
        return self.query(f'SENSE{channel:d}:FREQUENCY:STOP?', container=float)

    def set_center_freq(self, freq_hz: float, channel: int = 1):
        """ Set center frequency for channel.
        Args:
            freq_hz (float): Center freq in hertz
            channel (int): Channel number
        """
        self.write(f'SENSE{channel:d}:FREQUENCY:CENT {freq_hz:.0f}')

    def get_center_freq(self, channel: int = 1) -> float:
        """ Get center frequency for channel.
        Args:
            channel (int): Channel number
        Returns:
            float: Center freq in hertz
        """
        return self.query(f'SENSE{channel:d}:FREQUENCY:CENT?', container=float)

    def set_cw_freq(self, freq_hz: float, channel: int = 1):
        """ Set CW frequency for channel.
        Args:
            freq_hz (float): CW freq in hertz
            channel (int): Channel number
        """
        self.write(f'SENSE{channel:d}:FREQUENCY:CW {freq_hz:.0f}')

    def get_cw_freq(self, channel: int = 1) -> float:
        """ Get CW frequency for channel.
        Args:
            channel (int): Channel number
        Returns:
            float: CW freq in hertz
        """
        return self.query(f'SENSE{channel:d}:FREQUENCY:CW?', container=float)

    def set_number_sweep_points(self, num_points: Union[int, float], channel: int = 1):
        """ Set number sweep points for channel.
        Args:
            numPoints (int): Number sweep points
            channel (int): Channel number
        """
        self.write(f'SENSE{channel:d}:SWEEP:POINTS {num_points:d}')

    def get_number_sweep_points(self, channel: int = 1) -> int:
        """ Get number sweep points for channel.
        Args:
            channel (int): Channel number
        Returns:
            int: Number sweep points
        """
        return self.query(f'SENSE{channel:d}:SWEEP:POINTS?', container=int)

    def set_frequency_step_size(self, freq_hz: float, channel: int = 1):
        """ Set freq step size for channel.
        Args:
            freq_hz (float): Frequency step size in hertz
            channel (int): Channel number
        """
        self.write(f'SENSE{channel:d}:SWEEP:STEP {freq_hz:0.}')

    def get_frequency_step_size(self, channel: int = 1) -> float:
        """ Get frequency step size
        Args:
            channel (int): Channel number
        Returns:
            float: Frequency step size in hertz
        """
        return self.query(f'SENSE{channel:d}:SWEEP:STEP?', container=float)

    def set_sweep_type(self, sweep_type: str, channel: int = 1):
        """ Set sweep type.
        Args:
            sweepType (string): 'LINear | LOGarithmic | POWer | CW | SEGMent | PHASe'
            channel (int): Channel number
        """
        self.write(f'SENSE{channel:d}:SWEEP:TYPE {sweep_type:s}')

    def get_sweep_type(self, channel: int = 1) -> str:
        """ Get sweep type.
        Args:
            channel (int): Channel number
        Returns:
            str: Sweep type
        """
        return self.query(f'SENSE{channel:d}:SWEEP:TYPE?')

    def get_sweep_time(self, channel: int = 1) -> float:
        """ Get sweep time in seconds. """
        return self.query(f"SENSE{channel:d}:SWEEP:TIME?", container=float)

    def set_bandwidth(self, bwid: Union[int, str], channel: int = 1):
        """ Set IF bandwidth.
        Args:
            bwid (int|string): Bandwidth in hertz ('MIN', 'MAX')
            channel (int): Channel number
        """
        self.write(f'SENSE{channel:d}:BWID {bwid}')

    def get_bandwidth(self, channel: int = 1) -> int:
        """ Get IF bandwidth.
        Args:
            channel (int): Channel number
        Returns:
            int: Bandwidth in hertz
        """
        return int(self.query(f'SENSE{channel:d}:BWID?', container=float))

    def set_sweep_mode(self, mode: str, channel: int = 1):
        """ Set sweep mode.
            NOTE: For SINGle, this will wait for sweep to complete.
        Args:
            mode (str): One of HOLD | CONTinuous | GROups | SINGle
            channel (int): Channel number
        """
        # Must use write_async as it'll wait for sweep to complete.
        self.write_async(f'SENSE{channel:d}:SWEEP:MODE {mode:s}')

    def get_sweep_mode(self, channel: int = 1) -> str:
        """ Get sweep mode.
        Args:
            channel (int): Channel number
        Returns:
            str: Sweep mode
        """
        return self.query(f'SENSE{channel:d}:SWEEP:MODE?')

    def get_cal_sets(self, form: str = 'GUID', channel: int = 1) -> List[str]:
        """ Get saved cal set IDs from registry.
        Args:
            form (str): GUID or NAME
        """
        return self.query_ascii_values(message=f'SENSE{channel:d}:CORR:CSET:CAT? {form}', converter='s')

    def get_calset_description(self, channel: int = 1) -> str:
        """Get active calset description """
        return self.query(f"SENSE{channel:d}:CORR:CSET:DESC?")

    def get_calset_data(
            self, eterm: str, port_a: int = 1, port_b: int = 2, rec: Optional[str] = None, channel: int = 1,
            big_endian: bool = True) -> np.array:
        """ Get calset data. Supports binary mode.
        Args:
            eterm (str):
                EDIR- Directivity | portA- measured, portB- not used
                ESRM- Source Match | portA- measured, portB- not used
                ERFT- Reflection Tracking | portA- tracking, portB- not used
                ELDM- Load Match | portA- measured, portB source
                ETRT- Transmission Tracking | portA- receive port, portB- source port
                EXTLK- Crosstalk | portA- receive port, portB- source port
                ERSPT- Response Tracking | portA- not used, portB- not used
                ERSPI- Response Isolation | portA- not used, portB- not used
            port_a (int): Port A. If not used set to a valid port index
            port_b (int): Port B. If not used set to a valid port index
            rec (str): VNA Receiver. Required for eterm ERSPT and ERSPI
        """
        rec_str = f",'{rec}'" if rec else ""
        cmd = f"SENSE{channel:d}:CORR:CSET:DATA? {eterm},{port_a},{port_b}{rec_str}"
        dformat = self.get_data_format()
        if is_binary_format(dformat=dformat):
            return self.query_binary_values(
                message=cmd, is_big_endian=big_endian, datatype=get_binary_datatype(dformat=dformat),
                container=np.array, chunk_size=None
            )
        return self.query_ascii_values(message=cmd, container=np.array)

    def get_calset_eterm(self, eterm: str, channel: int = 1, big_endian: bool = True) -> List[str]:
        """Get calset eterm"""
        cmd = f"SENSE{channel}:CORR:CSET:ETER? '{eterm}'"
        dformat = self.get_data_format()
        if is_binary_format(dformat=dformat):
            return self.query_binary_values(
                message=cmd, is_big_endian=big_endian, datatype=get_binary_datatype(dformat=dformat),
                container=np.array, chunk_size=None
            )
        return self.query_ascii_values(message=cmd, container=np.array)

    def get_calset_eterm_names(self, channel: int = 1) -> List[str]:
        """Get calset eterm names. """
        result = self.query("SENSE{channel:d}:CORR:CSET:ETER:CAT?")
        # NOTE: Results return commas in eterm name as well as between eterms
        return result.replace("),", ");").split(';')

    def get_calset_name(self, channel: int = 1) -> str:
        """Get selected cal set name. """
        return self.query(f"SENSE{channel}:CORR:CSET:NAME?")

    def set_active_cal_set(
            self, cal_set: str, interpolate: bool = True, apply_cal_stimulus: bool = True, channel: int = 1):
        """ Select and applies cal set to specified channel
        Args:
            cal_set (str): Cal Set to make active
            interpolate (bool): Interpolate data points
            channel (int): Channel number
        """
        interpolate_cmd = 'ON' if interpolate else 'OFF'
        stimulus_cmd = '1' if apply_cal_stimulus else '0'
        self.write(f'SENSE{channel:d}:CORR:INT {interpolate_cmd}')
        self.write_async(f'SENSE{channel:d}:CORR:CSET:ACT \'{cal_set}\',{stimulus_cmd}')

    def deactive_active_cal_set(self, channel: int = 1):
        """ Disable active cal set. """
        self.write(f'SENSE{channel:d}:CORR:CSET:DEAC')

    # pylint: disable=too-many-arguments
    def setup_sweep(
            self, start_freq: float, stop_freq: float, num_points: Union[int, float],
            sweep_type: str = "LINEAR", channel: int = 1):
        """Convience method to configure common sweep parameters
        Args:
            start_freq (float): Start frequency in Hz
            stop_freq (float): Stop frequency in Hz
            num_points (int): Number frequency points
            sweep_type (str): Sweep type [see setSweepType()]
            channel (int): Channel number
        """
        self.set_start_freq(start_freq, channel=channel)
        self.set_stop_freq(stop_freq, channel=channel)
        self.set_number_sweep_points(num_points, channel=channel)
        self.set_sweep_type(sweep_type, channel=channel)
        self.sync_commands_nonblocking()

    def delete_all_traces(self, channel: int = 1):
        """ Delete all measurement traces. """
        self.write_async(f'CALC{channel:d}:PAR:DEL:ALL')

    def create_trace(self, tname: str, sname: str, channel: int = 1):
        """ Create measurement trace and select it. """
        self.write(f'CALC{channel:d}:PAR:DEF \'{tname}\',{sname}')
        self.write(f'CALC{channel:d}:PAR:SEL \'{tname}\'')
        self.sync_commands_nonblocking()

    def create_window_trace(self, window: int, trace: int, name: str):
        """ Create window trace and assign measurement trace feed. """
        self.write_async(f'DISP:WIND{window}:TRAC{trace}:FEED \'{name}\'')

    def set_display_window(self, window: int, on: bool):
        """ Set window on/off. """
        on_str = 'ON' if on else 'OFF'
        self.write_async(f'DISP:WIND{window}:STATE {on_str}')

    def get_trigger_source(self) -> str:
        """ Get trigger source. """
        return self.query('TRIG:SOUR?')

    def set_trigger_source(self, trigger_source: str = "IMM"):
        """ Set trigger source
        Args:
            trigger_source (str): Trigger source ['IMMEDIATE', 'CONTINUOUS']
        """
        self.write(f'TRIG:SOUR {trigger_source}')

    def set_trace_format(self, fmt: str = 'RI'):
        """ Setup SNP trace format
        Args:
            fmt (str): MA, DB, RI, AUTO"""
        self.write(f'MMEM:STOR:TRAC:FORM:SNP {fmt}')

    def set_data_format(self, dformat: str = 'real'):
        """ Set data format to be 'real,32' (binary), 'real,64' (binary), or 'ascii,0' """
        is_binary_fmt = dformat.startswith('real')
        is_64_bit = '64' in dformat
        fmt = 'REAL' if is_binary_fmt else 'ASCii'
        bits = '64' if is_64_bit else '32' if is_binary_fmt else '0'
        self.write(f'FORM:DATA {fmt},{bits}')

    def get_data_format(self) -> str:
        """ Get data format. """
        rsts = self.query('FORM:DATA?').split(',')
        # NOTE: Remove + from integer
        return rsts[0] + str(int(rsts[1]))

    def setup_ses_traces(self, port_pairs: Optional[Tuple[List[int], List[int]]] = None):
        """ Convenience method to setup single - ended sweep traces.
        Should be called after setting sweep params and mode.
        Args:
            port_pairs Optional[List[List[int]]]: Port pairs
        Returns:
            [str]: List of trace names
        """
        # Delete all measurements
        self.delete_all_traces()

        if port_pairs and len(port_pairs) != 2:
            raise ValueError('port_pairs must have length 2')

        # Default to all NxN pairs
        if port_pairs is None:
            port_pairs = 2 * [list(range(self.num_ports))]

        # Turn on windows
        for i, a in enumerate(port_pairs[0]):
            self.set_display_window(i + 1, on=True)

        # Create all single ended s-params w/ name ch1_s{i}{j}
        trace_names = []
        for i, a in enumerate(port_pairs[0]):
            for j, b in enumerate(port_pairs[1]):
                tname = f'CH1_S{a+1}{b+1}'
                sname = f'S{a+1}{b+1}'
                trace_names.append(tname)
                self.create_trace(tname, sname)
                self.create_window_trace(i + 1, j + 1, tname)
        self.set_trigger_source('IMMediate')
        return trace_names

    def capture_ses_traces(
            self, dtype=float, trace_names: Optional[List[str]] = None,
            port_pairs: Optional[Tuple[List[int], List[int]]] = None,
            big_endian: bool = True, sweep_mode: str = 'SINGLE'):
        """ Convenience method to capture single-ended measurement traces.
        Should be called after setup_ses_traces().
        Args:
            dtype: Data format either float or complex
            trace_names: Name of traces to capture
        Returns:
            Numpy.array: Numpy tensor with shape NxT if trace_names
            else NxSxS otherwise.
            T - Number of supplied traces
            N - 4 for single ended mode on 4 - port
            F - Number of sweep points
        """
        # Trigger trace and wait.
        self.set_sweep_mode(sweep_mode)

        # Get data format
        dformat = self.get_data_format()

        num_points = self.get_number_sweep_points()
        dtype_name = 'SDATA' if dtype == complex else 'FDATA'
        cmd = f'CALC1:DATA? {dtype_name}'
        data: np.array = np.array([])
        # Get only provided traces data as FxT Tensor
        if trace_names:
            sdata = np.zeros((num_points, len(trace_names)), dtype=dtype)
            for i, trace_name in enumerate(trace_names):
                self.write(f'CALC1:PAR:SEL \'{trace_name}\'')
                if is_binary_format(dformat=dformat):
                    chunk_size = num_points * 100  # 2000*1024
                    data: np.array = self.query_binary_values(
                        message=cmd, datatype=get_binary_datatype(dformat=dformat), is_big_endian=big_endian,
                        container=np.array, chunk_size=chunk_size
                    )
                else:
                    data: np.array = self.query_ascii_values(message=cmd, container=np.array)
                # Complex is returned as alternating real,imag,...
                if dtype == complex:
                    data = data[0::2] + 1j * data[1::2]  # type: ignore
                sdata[:, i] = data

        # Get all single-ended s-params
        else:
            # Default to all NxN pairs
            if port_pairs is None:
                port_pairs = 2 * [list(range(self.num_ports))]
            sdata = np.zeros((num_points, len(port_pairs[0]), len(port_pairs[1])), dtype=dtype)
            for i, a in enumerate(port_pairs[0]):
                for j, b in enumerate(port_pairs[1]):
                    self.write(f'CALC1:PAR:SEL \'CH1_S{a+1}{b+1}\'')
                    if is_binary_format(dformat=dformat):
                        chunk_size = num_points * 100  # 2000*1024
                        data: np.array = self.query_binary_values(
                            message=cmd, datatype=get_binary_datatype(dformat=dformat), is_big_endian=big_endian,
                            container=np.array, chunk_size=chunk_size
                        )
                    else:
                        data: np.array = self.query_ascii_values(message=cmd, container=np.array)
                    # Complex is returned as alternating real,imag,...
                    if dtype == complex:
                        data = data[0::2] + 1j * data[1::2]  # type: ignore
                    sdata[:, i, j] = data
        self.write('*CLS')  # Clean up
        return sdata

    def setup_snp_traces(self, ports: Optional[List[int]] = None):
        """ Setup SnP traces for given ports"""
        if ports is None:
            ports = list(range(self.num_ports))
        port_pairs = [ports, ports]
        return self.setup_ses_traces(port_pairs)

    def capture_snp_data(self, ports: Optional[List[int]] = None, big_endian: bool = True,
                         sweep_mode: str = 'SINGLE'):
        """ Capture SnP data for given ports in RI format.
        Args:
            ports: list of desired ports(base - 0 index)
            dformat: Data format for transfer: 'ascii', 'real', 'real,32', 'real,64'
        Returns:
            freq: np.array[npoints]
            sdata: np.array[npoints x  nports x nports]
        """
        if ports is None:
            ports = list(range(self.num_ports))
        nports = len(ports)

        # Trigger trace and wait.
        self.set_sweep_mode(sweep_mode)

        # Get data format
        dformat = self.get_data_format()

        # Read back real,imag format
        self.set_trace_format('RI')
        self.set_data_format(dformat)

        npoints = self.get_number_sweep_points()

        # Capture port data
        cmd = f"CALC:DATA:SNP:PORTs? \"{','.join(str(int(p)+1) for p in ports)}\""

        if is_binary_format(dformat=dformat):
            chunk_size = npoints * nports * nports * 10 * 2
            data: np.array = self.query_binary_values(
                message=cmd, datatype=get_binary_datatype(dformat=dformat), is_big_endian=big_endian,
                container=np.array, chunk_size=chunk_size
            )
        else:
            data: np.array = self.query_ascii_values(message=cmd, container=np.array)

        # Reshape 1-d array to 3-d tensor
        freq = data[:npoints]
        sdata = np.zeros((npoints, nports, nports), dtype=complex)
        for r in range(nports):
            for c in range(nports):
                r_idx = npoints + 2 * npoints * nports * r + 2 * npoints * c
                i_idx = r_idx + npoints
                sdata[:, r, c] = data[r_idx:i_idx] + 1j * data[i_idx:i_idx + npoints]  # type: ignore
        self.write('*CLS')  # Clean up
        return freq, sdata

    def setup_diff_traces(self):
        """ Convenience method to setup differential sweep traces for all
        diff s-params. Should be called after setting sweep params and mode.
        Args:
            None
        Returns:
            None
        """
        num_diff_pairs = self.num_ports // 2

        # Delete all measurements
        self.delete_all_traces()
        self.write('CALC1:FSIM:BAL:DEV BBALANCED')
        self.delete_all_traces()

        # Turn on N windows
        for i in range(num_diff_pairs * num_diff_pairs):
            self.set_display_window(i + 1, on=True)

        for i in range(num_diff_pairs):
            for j in range(num_diff_pairs):
                tname = f'sdd{i+1}{j+1}'
                tidx = 2 * i + j + 1
                self.create_trace(tname, f'S{i+1}{j+1}')
                self.write('CALC1:FSIM:BAL:PAR:STATE ON')
                self.write(f'CALC1:FSIM:BAL:PAR:BBAL:DEF \'{tname}\'')
                self.create_window_trace(tidx, tidx, tname)

        self.write('CALC1:FSIM:BAL:DEV BBALANCED')
        port_list = ','.join([str(p + 1) for p in range(self.num_ports)])
        self.write(f'CALC1:FSIM:BAL:TOP:BBAL:PPORTS {port_list}')
        self.set_trigger_source('IMMediate')

    def capture_diff_traces(self, dtype=float, sweep_mode: str = 'SINGLE', big_endian: bool = True):
        """ Convenience method to capture differential sweep traces for
        all diff s-params SDD11, SDD12, SDD21, ....
        Should be called after setupS4PTraces().
        Args:
            dtype: Data format either float or complex
        Returns:
            Numpy.array: Numpy tensor with shape NxSxS
            S - 2 for differential mode on 4 - port
            N - Number of sweep points
        """
        num_diff_pairs = self.num_ports // 2

        # Trigger trace and wait.
        self.set_sweep_mode(sweep_mode)

        # Get data format
        dformat = self.get_data_format()

        num_points = self.get_number_sweep_points()
        diff_data = np.zeros((num_points, num_diff_pairs, num_diff_pairs), dtype=dtype)

        dtype_name = 'SDATA' if dtype == complex else 'FDATA'
        cmd = f'CALC1:DATA? {dtype_name}'
        for i in range(num_diff_pairs):
            for j in range(num_diff_pairs):
                self.write(f'CALC1:PAR:SEL \'sdd{i+1}{j+1}\'')

                if is_binary_format(dformat=dformat):
                    chunk_size = num_points * 100
                    data: np.array = self.query_binary_values(
                        message=cmd, datatype=get_binary_datatype(dformat=dformat), is_big_endian=big_endian,
                        container=np.array, chunk_size=chunk_size
                    )
                else:
                    data: np.array = self.query_ascii_values(message=cmd, container=np.array)

                # Complex is returned as alternating real,imag,...
                if dtype == complex:
                    data = data[0::2] + 1j * data[1::2]  # type: ignore
                diff_data[:, i, j] = data
        return diff_data

    def get_ecal_kit_ids(self) -> List[int]:
        """" Get ecal kit ids connected to VNA.
        Returns:
            List[int]: Ids of ecal kits
        """
        ecal_kit_ids = [int(m) for m in str(self.query('SENSE:CORR:CKIT:ECAL:LIST?')).strip().split(',')]
        # If just single item w/ id of 0, then that means no ecals are connected
        if len(ecal_kit_ids) == 1 and ecal_kit_ids[0] == 0:
            ecal_kit_ids = []
        return ecal_kit_ids

    def get_ecal_kit_info(self, kit_id: int) -> Tuple[Dict[str, str], str]:
        """ Get kit info such as:
            * ModelNumber: str
            * SerialNumber: str
            * ConnectorType: str
            * Port[A-D]Connector: str
            * MinFreq: str[float]
            * MaxFreq: str[float]
            * NumberOfPoints: str[int]
            * Calibrated: Date [DD/MM/YYYY]
            * CharacterizedBy: str
        Args:
            id of kit as returned by get_ecal_kit_ids.
        Returns:
            Dict[str, str]: Attempt to parse info as key-value store
            str: Raw string info read from kit
        """
        ecal_info = str(self.query(f'SENSE:CORR:CKIT:ECAL{kit_id}:INF?'))
        ecal_dict: Dict[str, str] = dict()
        for r in ecal_info.replace('"', '').split(','):
            if r.strip():
                kv = r.split(':')
                ecal_dict[kv[0].strip()] = kv[-1].strip()
        return ecal_dict, ecal_info

    def setup_ecalibration(
            self, port_connectors: List[str],
            port_kits: List[str],
            port_thru_pairs: List[int] = None, auto_orient: bool = True):
        """ Convience method to perform guided calibration w / e - cal module
        Args:
            port_connectors([str]):
                Defines connection for each port.
                Index corresponds to(port number - 1).
                E.g. ['2.92 mm female', '2.92 mm female']
            port_kits([str]):
                Defines e - cal kit used for each port.
                Index corresponds to(port number - 1).
                E.g. ['N4692-60003 ECal 13226', 'N4692-60003 ECal 13226']
            port_thru_pairs([int], optional):
                Defines port pairs to perform cal on.
                Defaults to min required by VNA.
                E.g[1, 2, 1, 3, 1, 4, 2, 3, 2, 4, 3, 4]
            auto_orient(bool, optional)
                To auto determine port connection orientation
                Default is True
        """
        if not isinstance(port_connectors, list) or not isinstance(port_kits, list):
            raise Exception('port_connectors and portKits must be of type list')

        if len(port_connectors) != len(port_kits):
            raise Exception('port_connectors and portKits must have same length')

        if not isinstance(port_thru_pairs, list) or (port_thru_pairs and len(port_thru_pairs) % 2):
            raise Exception('port_thru_pairs must be a list of even length')

        # Set port connector (i.e. 2.92 mm female)
        cmd = 'SENSE1:CORR:COLL:GUID:CONN:PORT'
        for i, connector in enumerate(port_connectors):
            self.write(f'{cmd}{i+1} "{connector}"')

        # Set port e-cal kit (i.e. N4692-60003 ECal 13226)
        cmd = 'SENSE1:CORR:COLL:GUID:CKIT:PORT'
        for i, kit in enumerate(port_kits):
            self.write(f'{cmd}{i+1} "{kit}"')

        # Set auto orientation setting
        self.write(f"SENSE1:CORR:PREF:ECAL:ORI {'ON' if auto_orient else 'OFF'}")

        # Set port thru pairs or use default of VNA
        self.write('SENSE1:CORR:COLL:GUID:INIT')
        if port_thru_pairs:
            thru_pair_def = ','.join([str(thru) for thru in port_thru_pairs])
            self.write(f'SENSE1:CORR:COLL:GUID:THRU:PORTS {thru_pair_def}')
            self.write('SENSE1:CORR:COLL:GUID:INIT')

    def get_number_ecal_steps(self):
        """ Get total number e - cal steps to be performed.
        Must be called after setupECalibration().
        Args:
            None
        Returns:
            int: Number of e-cal steps
        """
        return self.query('SENSE1:CORR:COLL:GUID:STEPS?', container=int)

    def get_ecal_step_info(self, step: int):
        """ Get e-cal step description.
        Must be called after setupECalibration().
        Args:
            step(int): Index of e-cal step
        Returns:
            str: Description of e-cal step.
        """
        return self.query(f'SENSE1:CORR:COLL:GUID:DESC? {step+1}')

    def perform_ecal_step(self, step: int, save: bool = True, save_name: Optional[str] = None, delay: float = 2):
        """ Perform e-cal step. Should be done in order.
        Must be called after setupECalibration().
        Best used for asynchronous execution.
        For synchronous, use performECalSteps() iterator.
        Args:
            step(int): Index of e-cal step to perform.
            save(bool, optional): To save results if last step
        Returns:
            None
        """
        if step >= self.get_number_ecal_steps():
            return
        self.write_async(f'SENSE1:CORR:COLL:GUID:ACQ STAN{step + 1},ASYN', delay=0.4)
        time.sleep(delay)
        if step == (self.get_number_ecal_steps() - 1) and save:
            save_suffix = f'SAVE:CSET "{save_name}"' if save_name else 'SAVE'
            self.write(f'SENSE1:CORR:COLL:GUID:{save_suffix}')

    def perform_ecal_steps(self, save: bool = True, save_name: Optional[str] = None, delay: float = 5):
        """ Perform all e-cal steps as iterator.
        Must be called after setup_ecalibration().
        Best used for synchronous execution.
        >> > vna.setup_ecalibration(...)
        >> > for step_description in vna.perform_ecal_steps():
        >> > print(step_description)
        Args:
            None
        Yields:
            str: Description of next step
        Returns:
            None
        """
        num_steps = self.get_number_ecal_steps()
        i = 0
        while i < num_steps:
            msg = self.get_ecal_step_info(i)
            yield msg
            self.perform_ecal_step(i, save=save, save_name=save_name, delay=delay)
            i += 1

    def set_averaging_count(self, avg_count: int, channel: int = 1):
        """ Set # of measurements to combine for an average. """
        self.write(f"SENSE{channel}:AVER:COUN {avg_count}")

    def set_averaging_mode(self, avg_mode="SWEEP", channel: int = 1):
        """Set averaging mode. """
        self.write(f"SENSE{channel}:AVER:MODE {avg_mode}")

    def set_averaging_state(self, on: bool = True, channel: int = 1):
        """Set averaging state (on or off)"""
        self.write(f"SENSE{channel}:AVER:STATE {1 if on else 0}")

    # def set_calset_data(self, cnum=1, eterm="", portA=1, portB=2, param="", eterm_data=None, channel: int = 1):
    #     # """no help available"""
    #     # scpi_command = scpi_preprocess(":SENS{:}:CORR:CSET:DATA {:},{:},{:},{:},", cnum, eterm, portA, portB, param)
    #     # self.write_values(scpi_command, eterm_data)

    def set_calset_description(self, description: str = "", channel: int = 1):
        """Set active calset description. """
        self.write(f"SENSE{channel}:CORR:CSET:DESC '{description}'")

    # def set_calset_eterm(self, eterm: str, data: List[float], channel: int = 1):
    #     """no help available"""
    #     self.resource.write (f"SENSE{channel}:CORR:CSET:ETER '{eterm}',")
    #     self.resource.
    #     self.write_values(scpi_command, eterm_data)

    def set_calset_name(self, name: str, channel: int = 1):
        """ Set calset name. """
        self.write(f"SENSE{channel}:CORR:CSET:NAME '{name}'")

    def set_channel_correction_state(self, on: bool = True, channel: int = 1):
        """ Set channel correction state (on or off). """
        self.write(f"SENSE{channel}:CORR:STATE {1 if on else 0}")

    def set_create_calset(self, name: str, channel: int = 1):
        """ Create calset with name. """
        self.write(f"SENSE{channel}:CORR:CSET:CRE '{name}'")

    def set_create_measurement(self, name: str, param: str, channel: int = 1):
        """ Create measurement with name. """
        self.write(f"CALC{channel}:PAR:DEF:EXT '{name}','{param}'")

    # def set_data(self, fmt: str = "SDATA", data=None, channel: int = 1):
    #     """no help available"""
    #     self.write(f"CALC{channel}:DATA {:},", cnum, fmt)
    #     self.write_values(scpi_command, data)

    def set_delete_calset(self, name: str, channel: int = 1):
        """ Delete cal set with name. """
        self.write(f"SENSE{channel}:CORR:CSET:DEL '{name}'")

    def set_delete_meas(self, name: str, channel: int = 1):
        """ Delete measurement with name.  """
        self.write(f"CALC{channel}:PAR:DEL '{name}'")

    def set_display_format(self, fmt="MLOG", channel: int = 1):
        """Set plot display format. """
        self.write(f"CALC{channel}:FORM {fmt}")

    def set_display_onoff(self, on: bool = True):
        """Set display state"""
        self.write(f"DISP:ENAB {1 if on else 0}")

    def set_display_trace(self, wnum: int, tnum: int, name: str):
        """Add trace to window for given measurement"""
        self.write(f"DISP:WIND{wnum:d}:TRAC{tnum}:FEED '{name}'")

    def set_groups_count(self, cnum=1, groups_count=1, channel: int = 1):
        """Set groups count"""
        self.write(f"SENSE{channel}:SWE:GRO:COUN {groups_count}")

    def set_measurement_correction_state(self, on: bool = True, channel: int = 1):
        """Set measurement correction state. """
        self.write(f"CALC{channel}:CORR:STAT {1 if on else 0}")

    def set_save_calset(self, user: int = 1, channel: int = 1):
        """Save calset.
        Args:
            user (int): [0, 9]
        """
        self.write(f"SENSE{channel}:CORR:CSET:SAVE user{user:02d}")

    def set_selected_measurement(self, name: str = "", channel: int = 1):
        """Set selected measurement by name. """
        self.write(f"CALC{channel}:PAR:SEL '{name}'")

    def set_selected_measurement_by_number(self, mnum: int, channel: int = 1):
        """Set selected measurement by number. """
        self.write(f"CALC{channel}:PAR:MNUM {mnum:d}")

    def set_snp_format(self, dformat: str = "RI"):
        """Set SNP format. """
        self.write(f"MMEM:STOR:TRAC:FORM:SNP {dformat}")

    def get_active_calset(self, form: str = "NAME", channel: int = 1) -> str:
        """Get active calset by NAME or GUID """
        return self.query("SENSE{channel}:CORR:CSET:ACT? {form}")

    def get_active_channel(self) -> int:
        """Get active channel number"""
        return self.query("SYST:ACT:CHAN?", container=int)

    def get_available_channels(self) -> int:
        """Get available channels"""
        return self.query("SYST:CHAN:CAT?", container=int)

    def get_averaging_count(self, channel: int = 1) -> int:
        """Get measurement averaging count """
        return self.query(f"SENS{channel}:AVER:COUN?", container=int)

    def get_averaging_mode(self, channel: int = 1) -> str:
        """Get averaging mode """
        return self.query(f"SENSE{channel}:AVER:MODE?")

    def get_averaging_state(self, channel: int = 1) -> bool:
        """Get if averaging is enabled"""
        return bool(self.query("SENSE{channel}:AVER:STAT?", container=int))

    def get_channel_correction_state(self, channel: int = 1) -> bool:
        """Get if channel correction is on"""
        return bool(self.query("SENSE{channel}:CORR:STAT?", container=int))

    def get_data(self, fmt: str = "SDATA", channel: int = 1):
        """no help available"""
        return self.query(f"CALC{channel}:DATA? {fmt}")

    def get_display_format(self, channel: int = 1) -> str:
        """Get display format of selected measurement. """
        return self.query("CALC{channel}:FORM?")

    def get_display_on(self) -> bool:
        """Is display on. """
        return bool(self.query("DISP:ENAB?", container=int))

    def get_groups_count(self, channel: int = 1):
        """Get groups count"""
        return self.query(f"SENSE{channel}:SWE:GRO:COUN?", container=int)

    def get_measurement_correction_state(self, channel: int = 1):
        """Get measurement correction state. """
        return bool(self.query(f"CALC{channel}:CORR:STAT?", container=int))

    def get_measurement_name_from_number(self, mnum: int) -> str:
        """Get measurement name by its number. """
        return self.query(f"SYST:MEAS{mnum:d}:NAME?")

    def get_measurement_names(self, channel: int = 1):
        """Get measurement names"""
        return self.query_ascii_values(
            message=f"CALC{channel}:PAR:CAT:EXT?", converter='s', separator=','
        )

    def get_measurement_numbers(self, channel: int = 1) -> List[int]:
        """Get measurement numbers"""
        return self.query_ascii_values(
            message=f"SYST:MEAS:CAT? {channel}", converter='d', separator=','
        )

    def get_save_calset(self, channel: int = 1) -> str:
        """Gets last correction set saved"""
        return self.query(f"SENSE{channel}:CORR:CSET:SAVE?")

    def get_selected_measurement(self, channel: int = 1) -> str:
        """Get selected measurement"""
        return self.query(f"CALC{channel}:PAR:SEL?")

    def get_selected_measurement_by_number(self, channel: int = 1) -> int:
        """Get selected measurement by its number"""
        return self.query(f"CALC{channel}:PAR:MNUM?", container=int)

    def get_snp_data(self, ports=(1, 2), channel: int = 1, big_endian: bool = True):
        """Get SNP data """
        cmd = f"CALC{channel}:DATA:SNP:PORT? \"{','.join(str(p) for p in ports)}\""
        dformat = self.get_data_format()
        if is_binary_format(dformat=dformat):
            return self.query_binary_values(
                message=cmd, is_big_endian=big_endian, datatype=get_binary_datatype(dformat=dformat),
                container=np.array, chunk_size=None
            )
        return self.query_ascii_values(message=cmd, container=np.array)

    def get_snp_format(self) -> str:
        """Get SNP format: RI, """
        return self.query("MMEM:STOR:TRAC:FORM:SNP?")

    def get_sweep_data(self, channel: int = 1, big_endian: bool = True) -> np.array:
        """Get sweep x data (e.g. frequencies) """
        cmd = f"SENSE{channel}:X:VALUES?"
        dformat = self.get_data_format()
        if is_binary_format(dformat=dformat):
            return self.query_binary_values(
                message=cmd, is_big_endian=big_endian, datatype=get_binary_datatype(dformat=dformat),
                container=np.array, chunk_size=None
            )
        return self.query_ascii_values(message=cmd, container=np.array)

    def get_window_trace_numbers(self, window: int = 1) -> List[int]:
        """Get window trace numbers"""
        return self.query_ascii_values(message=f"DISP:WIND{window}:CAT?", converter='d', separator=',')


if __name__ == '__main__':
    print('Started')
    vna = KeysightVNA(bus_address="TCPIP::127.0.0.1::5020::SOCKET", num_ports=4)
    vna.open(write_term='\n', read_term='\n')
    print(vna.get_id())
    vna.setup_sweep(20.E6, 30.E6, 10, 'LINEAR')
    vna.setup_diff_traces()
    print(vna.capture_diff_traces())
    vna.close()
    print('Finished')
