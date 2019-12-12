""" KeysightVNA enables controlling various Keysight VNA/PNAs. """
from __future__ import print_function
import time
from typing import Union, Optional, List
import logging
import numpy as np
from pyvisainstrument.VisaResource import VisaResource
logger = logging.getLogger('VISA')

# pylint: disable=too-many-public-methods


class KeysightVNA(VisaResource):
    """ KeysightVNA enables controlling various Keysight VNA/PNAs. """

    def __init__(self, num_ports: int, *args, **kwargs):
        super(KeysightVNA, self).__init__(name='VNA', *args, **kwargs)
        self.num_ports = num_ports

    def set_start_freq(self, freq_hz: float, channel: int = 1):
        """ Set start frequency for channel.
        Args:
            freq_hz (float): Start freq in hertz
            channel (int): Channel number
        """
        self.write(f'SENSE{channel:d}:FREQUENCY:START {freq_hz:.0f}')

    def get_start_freq(self, channel: int = 1):
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

    def get_stop_freq(self, channel: int = 1):
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

    def get_center_freq(self, channel: int = 1):
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

    def get_cw_freq(self, channel: int = 1):
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

    def get_number_sweep_points(self, channel: int = 1):
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

    def get_frequency_step_size(self, channel: int = 1):
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
            sweepType (string): 'LINear | LOGarithmic | POWer | CW
                                 | SEGMent | PHASe'
            channel (int): Channel number
        """
        self.write(f'SENSE{channel:d}:SWEEP:TYPE {sweep_type:s}')

    def get_sweep_type(self, channel: int = 1):
        """ Get sweep type.
        Args:
            channel (int): Channel number
        Returns:
            str: Sweep type
        """
        return self.query(f'SENSE{channel:d}:SWEEP:TYPE?')

    def set_bandwidth(self, bwid: Union[int, str], channel: int = 1):
        """ Set IF bandwidth.
        Args:
            bwid (int|string): Bandwidth in hertz ('MIN', 'MAX')
            channel (int): Channel number
        """
        self.write(f'SENSE{channel:d}:BWID {bwid}')

    def get_bandwidth(self, channel: int = 1):
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
        return str(self.query(f'SENSE{channel:d}:SWEEP:MODE?'))

    def get_cal_sets(self, channel: int = 1) -> List[str]:
        """ Get saved cal set IDs from registry. """
        cal_sets: str = str(self.query(f'SENSE{channel}:CORR:CSET:CAT?'))
        return cal_sets.split(',')

    def set_active_cal_set(
            self, cal_set: str, interpolate: bool = True, apply_cal_stimulus: bool = True, channel: int = 1):
        """ Select and applies cal set to specified channel
        Can get list of cal sets with SENS:CORR:CSET:CAT?
        Args:
            cal_set (str): Cal Set to make active
            interpolate (bool): Interpolate data points
            channel (int): Channel number
        """
        interpolate_cmd = 'ON' if interpolate else 'OFF'
        stimulus_cmd = '1' if apply_cal_stimulus else '0'
        self.write(f'SENSE{channel}:CORR:INT {interpolate_cmd}')
        self.write_async(f'SENSE{channel}:CORR:CSET:ACT \'{cal_set}\',{stimulus_cmd}')

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

    def delete_all_traces(self, cnum: int = 1):
        """ Delete all measurement traces. """
        self.write_async(f'CALC{cnum}:PAR:DEL:ALL')

    def create_trace(self, tname: str, sname: str, cnum: int = 1):
        """ Create measurement trace and select it. """
        self.write(f'CALC{cnum}:PAR:DEF \'{tname}\',{sname}')
        self.write(f'CALC{cnum}:PAR:SEL \'{tname}\'')
        self.sync_commands_nonblocking()

    def create_window_trace(self, window: int, trace: int, tname: str):
        """ Create window trace and assign measurement trace feed. """
        self.write_async(f'DISP:WIND{window}:TRAC{trace}:FEED \'{tname}\'')

    def set_display_window(self, window: int, on: bool):
        """ Set window on/off. """
        on_str = 'ON' if on else 'OFF'
        self.write_async(f'DISP:WIND{window}:STATE {on_str}')

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

    def setup_ses_traces(self, port_pairs: Optional[List[List[int]]] = None):
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
            self, dtype=float, trace_names: Optional[List[str]] = None, port_pairs: Optional[List[List[int]]] = None,
            data_format: str = 'real', big_endian: bool = True):
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
        self.set_sweep_mode('SINGLE')

        # Set data format
        self.set_data_format(data_format)

        num_points = self.get_number_sweep_points()
        dtype_name = 'SDATA' if dtype == complex else 'FDATA'
        data_query = f'CALC1:DATA? {dtype_name}'
        data: np.array = np.array([])
        # Get only provided traces data as FxT Tensor
        if trace_names:
            sdata = np.zeros((num_points, len(trace_names)), dtype=dtype)
            for i, trace_name in enumerate(trace_names):
                self.write(f'CALC1:PAR:SEL \'{trace_name}\'')
                if data_format.startswith('real'):
                    chunk_size = num_points * 100  # 2000*1024
                    data: np.array = self.query(
                        data_query, container=np.array, dformat=data_format,
                        big_endian=big_endian, chunk_size=chunk_size
                    )
                else:
                    data: np.array = self.query(data_query, container=np.ndarray)
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
                    if data_format.startswith('real'):
                        chunk_size = num_points * 100  # 2000*1024
                        data: np.array = self.query(
                            data_query, container=np.array, dformat=data_format,
                            big_endian=big_endian, chunk_size=chunk_size
                        )
                    else:
                        data: np.array = self.query(data_query, container=np.ndarray)
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

    def capture_snp_data(self, ports: Optional[List[int]] = None, dformat: str = 'real', big_endian: bool = True):
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
        self.set_sweep_mode('SINGLE')

        # Read back real,imag format
        self.set_trace_format('RI')
        self.set_data_format(dformat)
        npoints = self.get_number_sweep_points()
        # Capture port data
        dquery = f"CALC:DATA:SNP:PORTs? \"{','.join(str(int(p)+1) for p in ports)}\""
        chunk_size = npoints * nports * nports * 10 * 2
        data: np.array = self.query(
            dquery, container=np.array, dformat=dformat, big_endian=big_endian, chunk_size=chunk_size
        )
        # Reshape 1-d array to 3-d tensor
        freq = data[:npoints]
        sdata = np.zeros((npoints, nports, nports), dtype=np.complex)
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

    def capture_diff_traces(self, dtype=float):
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
        self.set_sweep_mode('SINGLE')
        num_points = self.get_number_sweep_points()
        diff_data = np.zeros((num_points, num_diff_pairs, num_diff_pairs), dtype=dtype)

        dtype_name = 'SDATA' if dtype == complex else 'FDATA'
        data_query = f'CALC1:DATA? {dtype_name}'
        for i in range(num_diff_pairs):
            for j in range(num_diff_pairs):
                self.write(f'CALC1:PAR:SEL \'sdd{i+1}{j+1}\'')
                data: np.array = self.query(data_query, container=np.ndarray)
                # Complex is returned as alternating real,imag,...
                if dtype == complex:
                    data = data[0::2] + 1j * data[1::2]  # type: ignore
                diff_data[:, i, j] = data
        return diff_data

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
