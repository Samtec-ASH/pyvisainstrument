import pytest  # NOQA
from multiprocessing import Process, Value
import threading
from ctypes import c_bool
import time
from pyvisainstrument import KeysightVNA
from pyvisainstrument.testsuite import DummyVNA


class TestKeysightVNA:

    def setup_class(self):
        inst_addr = 'TCPIP::{0}::{1}::SOCKET'.format('localhost', 5051)
        self.device = DummyVNA(num_ports=4, bus_address=inst_addr)
        self.device.open(read_term='\n', write_term='\n')
        self.device.start()
        self.vna = KeysightVNA(num_ports=4, bus_address=inst_addr, delay=2e-2)
        self.vna.open(read_term='\n', write_term='\n')

    def teardown_class(self):
        self.vna.close()
        self.vna = None

        self.device.close()
        self.device.join()

    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    def test_get_id(self):
        id = self.vna.get_id()
        assert isinstance(id, str)

    def test_set_sweep(self):
        self.vna.setup_sweep(
            1E7,
            2E10,
            20,
            sweep_type="LINEAR",
            channel=1
        )
        start_freq = self.vna.get_start_freq()
        stop_freq = self.vna.get_stop_freq()
        sweep_points = self.vna.get_number_sweep_points()
        sweep_type = self.vna.get_sweep_type()
        port_pairs = [[0, 1, 2, 3], [0, 1, 2, 3]]
        _ = self.vna.setup_ses_traces(port_pairs=port_pairs)
        # sData = self.vna.captureSESTrace(dtype=complex, portPairs=portPairs)
        _, sData = self.vna.capture_snp_data(ports=port_pairs[0])
        print(sData.shape)
        assert start_freq == 1E7
        assert stop_freq == 2E10
        assert sweep_points == 20
        assert sweep_type == "LINEAR"

    def test_perform_ecal(self):
        self.vna.setup_sweep(
            1E7,
            2E10,
            2000,
            sweep_type="LINEAR",
            channel=1
        )
        self.vna.setup_ecalibration(
            port_connectors=['2.92 mm female' for i in range(4)],
            port_kits=['N4692-60003 ECal 13226' for i in range(4)],
            port_thru_pairs=[1, 2, 1, 3, 1, 4],
            auto_orient=True
        )
        num_steps = self.vna.get_number_ecal_steps()
        steps = [self.vna.get_ecal_step_info(step) for step in range(num_steps)]
        for i, step in enumerate(steps):
            self.vna.perform_ecal_step(i, save=True, delay=0)
        assert True
