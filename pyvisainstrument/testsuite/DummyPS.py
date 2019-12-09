
# pylint: skip-file
from pyvisainstrument.testsuite.DummyTCPInstrument import DummyTCPInstrument


class DummyPS(DummyTCPInstrument):

    def __init__(self, *args, **kwargs):
        super(DummyPS, self).__init__(*args, **kwargs)
        self.MAX_VOLT = 24
        self.MIN_VOLT = 0
        self.MAX_CURR = 5
        self.MIN_CURR = 0
        self.OUTPUT_ID = dict(P6V=1, P25V=2, N25V=3, OUTP1=1, OUTP2=2)
        self.state = {
            "*IDN": "PS",
            "*OPC": "1",
            "*CLS": self.clear_status,
            "*RST": self.reset,
            "*ESR": "1",
            1: {
                "MEASURE": dict(VOLTAGE=dict(DC=0), CURRENT=dict(DC=0)),
                "OUTPUT": dict(STATE="OFF"),
                "VOLTAGE": dict(MIN="0", MAX="24", SET="0"),
                "CURRENT": dict(MIN="0", MAX="5", SET="5")
            },
            2: {
                "MEASURE": dict(VOLTAGE=dict(DC=0), CURRENT=dict(DC=0)),
                "OUTPUT": dict(STATE="OFF"),
                "VOLTAGE": dict(MIN="0", MAX="24", SET="0"),
                "CURRENT": dict(MIN="0", MAX="5", SET="5")
            },
            3: {
                "MEASURE": dict(VOLTAGE=dict(DC=0), CURRENT=dict(DC=0)),
                "OUTPUT": dict(STATE="OFF"),
                "VOLTAGE": dict(MIN="0", MAX="24", SET="0"),
                "CURRENT": dict(MIN="0", MAX="5", SET="5")
            },
            "VOLTAGE": self._voltage_set_point_handler,
            "CURRENT": self._current_limit_handler,
            "DISPLAY": dict(TEXT=dict(DATA="", CLEAR=None)),
            "INSTRUMENT": dict(NSELECT=1, SELECT="P6V")
        }
        self.map_commands = dict(
            APPL='APPLY', APPLY='APPLY',
            INST='INSTRUMENT', INSTRUMENT='INSTRUMENT',
            MEAS='MEASURE', MEASURE='MEASURE',
            OUTP='OUTPUT', OUTPUT='OUTPUT',
            CURR='CURRENT', CURRENT='CURRENT',
            VOLT='VOLTAGE', VOLTAGE='VOLTAGE',
            SEL='SELECT', SELECT='SELECT',
            NSEL='NSELECT', NSELECT='NSELECT',
            COUP='COUPLE', COUPLE='COUPLE',
            TRIG='TRIGGER', TRIGGER='TRIGGER',
            SCAL='SCALAR', SCALAR='SCALAR',
            TRAC='TRACK', TRACK='TRACK',
            STAT='STATE', STATE='STATE',
            LEV='LEVEL', LEVEL='LEVEL',
            PROT='PROTECTION', PROTECTION='PROTECTION',
            IMM='IMMEDIATE', IMMEDIATE='IMMEDIATE',
            AMPL='AMPLITUDE', AMPLITUDE='AMPLITUDE',
            INCR='INCREMENT', INCREMENT='INCREMENT',
            TRIP='TRIPPED', TRIPPED='TRIPPED',
            CLE='CLEAR', CLEAR='CLEAR',
            RANG='RANGE', RANGE='RANGE',
            DEF='DEFAULT', DEFAULT='DEFAULT',
            INIT='INITIATE', INITIATE='INITIATE',
            DEL='DELAY', DELAY='DELAY',
            SEQ='SEQUENCE', SEQUENCE='SEQUENCE',
            SOUR='SOURCE', SOURCE='SOURCE',
            REL='RELAY', RELAY='RELAY',
            BEEP='BEEPER', BEEPER='BEEPER',
            ERR='ERROR', ERROR='ERROR',
            WIND='WINDOW', WINDOW='WINDOW',
            VERS='VERSION', VERSION='VERSION'
        )

    def _voltage_set_point_handler(self, params, is_query):
        if is_query:
            field_name = params[0] if len(params) else "SET"
            return self.state[int(self._curr_inst())]["VOLTAGE"][field_name]
        else:
            self.state[int(self._curr_inst())]["VOLTAGE"]["SET"] = params[0]
            self.state[int(self._curr_inst())]["MEASURE"]["VOLTAGE"]["DC"] = params[0]
            return None

    def _current_limit_handler(self, params, is_query):
        if is_query:
            field_name = params[0] if len(params) else "SET"
            return self.state[int(self._curr_inst())]["CURRENT"][field_name]
        else:
            self.state[int(self._curr_inst())]["CURRENT"]["SET"] = params[0]
            return None

    def _curr_inst(self):
        return self.state["INSTRUMENT"]["NSELECT"]

    def clear_status(self, params, is_query):
        return

    def reset(self, params, is_query):
        return

    def process_query(self, state, value, cmd, params):
        if callable(value):
            return value(params, True)
        elif isinstance(value, dict) and len(params):
            return value.get(params[0], "-100")
        elif type(value) in [str, int, float, bool]:
            return str(value)
        else:
            return '-100'

    def process_write(self, state, value, cmd, params):
        if callable(value):
            return value(params, False)
        if type(state) is dict and type(value) in [str, int, float, bool]:
            if len(params):
                castType = type(params[0]) if value is None else type(value)
                state[cmd] = castType(params[0])
            return None
        else:
            raise Exception('Unknown command')

    def process_command(self, cmd_tree, params, is_query):
        mapped_cmd_tree = [self.map_commands.get(cmd, cmd) for cmd in cmd_tree]
        rootCmd = mapped_cmd_tree[0]
        if rootCmd in ['MEASURE', 'OUTPUT']:
            state_head = self.state[self._curr_inst()]
        else:
            state_head = self.state
        state_leaf = state_head
        pcmd = None
        for cmd in mapped_cmd_tree:
            if cmd in state_leaf:
                state_head = state_leaf
                state_leaf = state_head[cmd]
                pcmd = cmd
            else:
                break
        if is_query:
            return self.process_query(state_head, state_leaf, pcmd, params)
        else:
            return self.process_write(state_head, state_leaf, pcmd, params)
