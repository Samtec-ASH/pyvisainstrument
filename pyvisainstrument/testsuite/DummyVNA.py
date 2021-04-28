# pylint: skip-file
import random
from typing import Optional, Dict
import numpy as np
from pyvisainstrument.testsuite.DummyTCPInstrument import DummyTCPInstrument


class DummyVNA(DummyTCPInstrument):

    def __init__(self, num_ports=4, *args, **kwargs):
        super(DummyVNA, self).__init__(*args, **kwargs)
        self.num_ports = num_ports
        self.cmd_tree = None
        self.state = {
            "*CLS": self.clear_status,
            "*RST": self.reset,
            "*IDN": "VNA",
            "*OPC": "1",
            "*ESR": "1",
            "SENSE": {
                "X": {
                    "VALUES": self._get_x_data
                },
                "AVERAGE": {
                    "STATE": 1,
                    "MODE": "SWEEP",
                    "COUNT": 1
                },
                "BWIDTH": "1000",
                "FREQUENCY": {
                    "START": "1E7",
                    "STOP": "2E10",
                    "CENTER": "5E8",
                    "CW": "5E8"
                },
                "SWEEP": {
                    "POINTS": "2000",
                    "STEP": "1E7",
                    "TYPE": "LINEAR",
                    "POWER": "10",
                    "MODE": "SINGLE",
                    "TIME": "0.1"
                },
                "CORRECTION": {
                    "CSET": {
                        "ACTIVATE": "",
                        "DEACTIVATE": "",
                        "CATALOG": "calset1,calset2",
                        "DESCRIPTION": "A calset description.",
                        "DATA": "1,2,3,4,5",
                        "ETERM": "Directivity(1,1)",
                        "NAME": "calset1",
                        "CREATE": ""
                    },
                    "STATE": 1,
                    "COLLECTION": {
                        "GUIDED": {
                            "STEPS": "3",
                            "DESCRIPTION": self.get_ecal_description,
                            "CONNECTOR": {
                                "PORT1": "",
                                "PORT2": "",
                                "PORT3": "",
                                "PORT4": ""
                            },
                            "CKIT": {
                                "PORT1": "",
                                "PORT2": "",
                                "PORT3": "",
                                "PORT4": ""
                            },
                            "ACQUIRE": None,
                            "SAVE": {"CSET": None},
                            "THRU": {"PORTS": [1, 2, 1, 3, 1, 4]},
                            "INITIATE": "+1"
                        }
                    },
                    "INTERPOLATE": "ON",
                    "PREFERENCE": {"ECAL": {"ORIENTATION": "ON"}},
                    "CKIT": {
                        "ECAL": {
                            "LIST": "+1"
                        },
                        "ECAL1": {
                            "INF": '"ModelNumber: N4691-60006, SerialNumber: 16194, ConnectorType: 35F 35F, PortAConnector: APC 3.5 female, PortBConnector: APC 3.5 female, MinFreq: 300000, MaxFreq: 26500000000, NumberOfPoints: 583, Calibrated: 19/Sep/2018, CharacterizedBy: 15N5239932, "\n'
                        }
                    }
                }
            },
            "CALCULATE": {
                "PARAMETER": {
                    "DELETE": {"ALL": None},
                    "DEFINE": "'sdd11',S11",
                    "SELECT": "'sdd11'",
                },
                "FSIMULATOR": {
                    "BALUN": {
                        "DEVICE": None,
                        "TOPOLOGY": {"BBALANCED": {"PPORTS": "1,2,3,4"}},
                        "PARAMETER": {"STATE": "ON", "BBALANCED": {"DEFINE": "SDD11"}}
                    }
                },
                "DATA": self._get_data,
                "FORMAT": "MLOG"
            },
            "DISPLAY": {
                "ENABLE": 1,
                "WIND1": {
                    "TRAC1": {"FEED": "sdd11"},
                    "TRAC2": {"FEED": "sdd12"},
                    "TRAC3": {"FEED": "sdd21"},
                    "TRAC4": {"FEED": "sdd22"},
                    "STATE": "OFF"
                },
                "WIND2": {
                    "TRAC1": {"FEED": "sdd11"},
                    "TRAC2": {"FEED": "sdd12"},
                    "TRAC3": {"FEED": "sdd21"},
                    "TRAC4": {"FEED": "sdd22"},
                    "STATE": "OFF"
                },
                "WIND3": {
                    "TRAC1": {"FEED": "sdd11"},
                    "TRAC2": {"FEED": "sdd12"},
                    "TRAC3": {"FEED": "sdd21"},
                    "TRAC4": {"FEED": "sdd22"},
                    "STATE": "OFF"
                },
                "WIND4": {
                    "TRAC1": {"FEED": "sdd11"},
                    "TRAC2": {"FEED": "sdd12"},
                    "TRAC3": {"FEED": "sdd21"},
                    "TRAC4": {"FEED": "sdd22"},
                    "STATE": "OFF"
                }
            },
            "TRIGGER": {
                "SOURCE": "IMMediate"
            },
            "MMEMORY": {
                "STORE": {
                    "TRACE": {
                        "FORMAT": {
                            "SNP": "RI"
                        }
                    }
                }
            },
            "FORMAT": {
                "DATA": "ASCii,+0"
            }
        }
        self.map_commands = dict(
            CALC1='CALCULATE', CALCULATE1='CALCULATE',
            SENS1='SENSE', SENSE1='SENSE',
            CALC='CALCULATE', CALCULATE='CALCULATE',
            CALP='CALPOD', CALPOD='CALPOD',
            CONT='CONTROL', CONTROL='CONTROL',
            DISP='DISPLAY', DISPLAY='DISPLAY',
            DEAC='DEACTIVATE', DEACTIVATE='DEACTIVATE',
            FORM='FORMAT', FORMAT='FORMAT',
            HCOP='HCOPY', HCOPY='HCOPY',
            INIT='INITIATE', INITIATE='INITIATE',
            MMEM='MMEMORY', MMEMORY='MMEMORY',
            OUTP='OUTPUT', OUTPUT='OUTPUT',
            ROUT='ROUTE', ROUTE='ROUTE',
            SENS='SENSE', SENSE='SENSE',
            STAT='STATUS', STATUS='STATUS',
            SYST='SYSTEM', SYSTEM='SYSTEM',
            TRIG='TRIGGER', TRIGGER='TRIGGER',
            CORR='CORRECTION', CORRECTION='CORRECTION',
            CUST='CUSTOM', CUSTOM='CUSTOM',
            EQU='EQUATION', EQUATION='EQUATION',
            FILT='FILTER', FILTER='FILTER',
            FSIM='FSIMULATOR', FSIMULATOR='FSIMULATOR',
            FUNC='FUNCTION', FUNCTION='FUNCTION',
            GDELA='GDELAY', GDELAY='GDELAY',
            LIM='LIMIT', LIMIT='LIMIT',
            MARK='MARKER', MARKER='MARKER',
            MIX='MIXER', MIXER='MIXER',
            NORM='NORMALIZE', NORMALIZE='NORMALIZE',
            OFFSet='OFFSET', OFFSET='OFFSET',
            PAR='PARAMETER', PARAMETER='PARAMETER',
            RDAT='RDATA', RDATA='RDATA',
            DATA='DATA', SDATA='SDATA',
            SMO='SMOOTHING', SMOOTHING='SMOOTHING',
            TRANS='TRANSFORM', TRANSFORM='TRANSFORM',
            UNC='UNCERTAINTY', UNCERTAINTY='UNCERTAINTY',
            COLL='COLLECTION', COLLECTION='COLLECTION',
            GUID='GUIDED', GUIDED='GUIDED',
            ABOR='ABORT', ABORT='ABORT',
            DEL='DELETE', DELETE='DELETE',
            DEF='DEFINE', DEFINE='DEFINE',
            CAT='CATALOG', CATALOG='CATALOG',
            MOD='MODIFY', MODIFY='MODIFY',
            SEL='SELECT', SELECT='SELECT',
            EXT='EXTENDED', EXTENDED='EXTENDED',
            DESC='DESCRIPTION', DESCRIPTION='DESCRIPTION',
            CONN='CONNECTOR', CONNECTOR='CONNECTOR',
            ACQ='ACQUIRE', ACQUIRE='ACQUIRE',
            CHAN='CHANNEL', CHANNEL='CHANNEL',
            PORT='PORTS', PORTS='PORTS',
            ACT='ACTIVATE', ACTIVATE='ACTIVATE',
            PREF='PREFERENCE', PREFERENCE='PREFERENCE',
            ORI='ORIENTATION', ORIENTATION='ORIENTATION',
            BAL='BALUN', BALUN='BALUN',
            DEV='DEVICE', DEVICE='DEVICE',
            TOP='TOPOLOGY', TOPOLOGY='TOPOLOGY',
            BBAL='BBALANCED', BBALANCED='BBALANCED',
            PPOR='PPORTS', PPORTS='PPORTS',
            POINT='POINTS', POINTS='POINTS',
            PORT1='PORT1', PORT2='PORT2',
            PORT3='PORT3', PORT4='PORT4',
            THRU='THRU', STEPS='STEPS',
            SOUR='SOURCE', SOURCE='SOURCE',
            CSET='CSET', INT='INTERPOLATE',
            COUN='COUNT', COUNT='COUNT',
            SNP='SNP',
            BWID='BWIDTH', BWIDTH='BWIDTH',
            BAND='BWIDTH', BANDWIDTH='BWIDTH',
            ETERM="ETERM", ETER="ETERM",
            WIND='WINDOW', WINDOW='WINDOW',
            TRAC='TRACE', TRACE='TRACE',
            STOR='STORE', STORE='STORE',
            AVER='AVERAGE', AVERAGE='AVERAGE',
            CRE='CREATE', CREATE='CREATE',
            ENAB='ENABLE', ENABLE='ENABLE',
        )

    def _get_x_data(self, params, is_query):
        if is_query:
            num_points = int(float(self.state["SENSE"]["SWEEP"]["POINTS"]))
            s_type = self.state["SENSE"]["SWEEP"]["TYPE"]
            f_start = float(self.state["SENSE"]["FREQUENCY"]["START"])
            f_stop = float(self.state["SENSE"]["FREQUENCY"]["STOP"])
            if s_type.upper().startswith('LIN'):
                data = np.linspace(f_start, f_stop, num_points)
            elif s_type.upper().startswith('LOG'):
                data = np.logspace(f_start, f_stop, num_points)
            else:
                data = np.linspace(f_start, f_stop, num_points)
            return ",".join('{:+.6E}'.format(v) for v in data)

    def _get_data(self, params, is_query):
        if is_query:
            num_points = int(float(self.state["SENSE"]["SWEEP"]["POINTS"]))
            # CALC:DATA:SNP:PORTs 1,2,3,4?
            if self.cmd_tree and 'SNP' in self.cmd_tree:
                nports = len(params[0].split(',')) if len(params) else self.num_ports
                #           freq + S11r,i + S12r,i, ... S22r,i ... SNNr,i
                num_points = num_points + num_points * (nports**2) * 2
            else:
                is_complex = len(params) and (params[0] in ["RDATA", "SDATA"])
                if is_complex:
                    num_points = 2 * num_points
            data = np.random.rand(num_points)
            data_str = ",".join('{:+.6E}'.format(v) for v in data)
            return data_str

    def clear_status(self, params, is_query):
        return

    def reset(self, params, is_query):
        return

    def get_ecal_description(self, params, is_query):
        ports = list(np.random.permutation(range(self.num_ports))[:2])
        return "Please connect e-cal module from port {} to port {}".format(ports[0] + 1, ports[-1] + 1)

    def process_command(self, cmd_tree, params, is_query):
        self.cmd_tree = cmd_tree
        rst = self.state
        prst: Optional[Dict] = None
        pcmd = None
        for cmd in cmd_tree:
            mapped_cmd = self.map_commands.get(cmd, cmd)
            if mapped_cmd in rst:
                prst = rst
                pcmd = mapped_cmd
                rst = rst[mapped_cmd]
                if callable(rst):
                    break
            else:
                break

        if is_query:
            if type(rst) in [str, int, float, bool]:
                return str(rst)
            elif type(rst) is None:
                return ''
            elif callable(rst):
                return rst(params, True)  # type: ignore
            else:
                return '-100'
        else:
            if callable(rst):
                rst(params, False)  # type: ignore
            elif isinstance(prst, dict) and (isinstance(rst, (str, int, float, bool, list)) or rst is None):
                if len(params):
                    castType = type(params[0]) if rst is None else type(prst[pcmd])
                    prst[pcmd] = castType(params[0])
                return None
            else:
                raise Exception('Unknown command')
