# pylint: skip-file
import numpy as np
from pyvisainstrument.testsuite.DummyTCPInstrument import DummyTCPInstrument


class DummyVNA(DummyTCPInstrument):

    def __init__(self, numPorts=4, *args, **kwargs):
        super(DummyVNA, self).__init__(*args, **kwargs)
        self.numPorts = numPorts
        self.state = {
            "*CLS": self.clearStatus,
            "*RST": self.reset,
            "*IDN": "VNA",
            "*OPC": "1",
            "*ESR": "1",
            "SENSE": {
                "FREQUENCY": {
                    "START": "1E7",
                    "STOP": "1E9",
                    "CENTER": "5E8",
                    "CW": "5E8"
                },
                "SWEEP": {
                    "POINTS": "100",
                    "STEP": "100",
                    "TYPE": "LINEAR",
                    "POWER": "10",
                    "MODE": "SINGLE"
                },
                "CORRECTION": {
                    "CSET": {"ACTIVATE": ""},
                    "COLLECTION": {
                        "GUIDED": {
                            "STEPS": "3",
                            "DESCRIPTION": "Please do blah for step blah",
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
                    "PREFERENCE": {"ECAL": {"ORIENTATION": "ON"}}
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
                "DATA": self._getData
            },
            "DISPLAY": {
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
            }
        }
        self.mapCommands = dict(
            CALC1='CALCULATE', CALCULATE1='CALCULATE',
            SENS1='SENSE', SENSE1='SENSE',
            CALC='CALCULATE', CALCULATE='CALCULATE',
            CALP='CALPOD', CALPOD='CALPOD',
            CONT='CONTROL', CONTROL='CONTROL',
            DISP='DISPLAY', DISPLAY='DISPLAY',
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
            CSET='CSET', INT='INTERPOLATE'
        )

    def _getData(self, params, isQuery):
        if isQuery:
            isComplex = len(params) and (params[0] in ["RDATA", "SDATA"])
            numPoints = int(self.state["SENSE"]["SWEEP"]["POINTS"])
            if isComplex:
                numPoints = 2*numPoints
            data = np.random.rand(numPoints)
            dataStr = ",".join('{:+.6E}'.format(v) for v in data)
            return dataStr

    def clearStatus(self, params, isQuery):
        return

    def reset(self, params, isQuery):
        return

    def processCommand(self, cmdTree, params, isQuery):
        rst = self.state
        prst = None
        pcmd = None
        for cmd in cmdTree:
            mappedCmd = self.mapCommands.get(cmd, cmd)
            if mappedCmd in rst:
                prst = rst
                pcmd = mappedCmd
                rst = rst[mappedCmd]
            else:
                break

        if isQuery:
            if type(rst) in [str, int, float, bool]:
                return str(rst)
            elif type(rst) is None:
                return ''
            elif callable(rst):
                return rst(params, True)
            else:
                return '-100'
        else:
            if callable(rst):
                rst(params, False)
            elif type(prst) is dict and (type(rst) in [str, int, float, bool, list] or rst is None):
                if len(params):
                    castType = type(params[0]) if rst is None else type(prst[pcmd])
                    prst[pcmd] = castType(params[0])
                return None
            else:
                raise Exception('Unknown command')
