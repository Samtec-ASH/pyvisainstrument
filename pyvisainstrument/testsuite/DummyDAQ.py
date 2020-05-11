# pylint: skip-file
import re
from typing import List, Union, Dict
from pyvisainstrument.testsuite.DummyTCPInstrument import DummyTCPInstrument


class DummyDAQ(DummyTCPInstrument):

    def __init__(self, *args, **kwargs):
        super(DummyDAQ, self).__init__(*args, **kwargs)
        self.num_slots = kwargs['num_slots']
        self.num_channels = kwargs['num_channels']
        open_state = [int(f'{s:01d}{c:02d}') for s in range(1, 1 + self.num_slots)
                      for c in range(1, 1 + self.num_channels)]
        self.state = {
            "*CLS": self.clear_status,
            "*RST": self.reset,
            "*IDN": "34970A",
            "*OPC": "1",
            "*ESR": "1",
            "ROUTE": {
                "OPEN": open_state,
                "CLOSE": [],
                "DONE": "1"
            },
            "MEASURE": {
                "TEMPERATURE": "+2.12340000E+01",
                "RHUMIDITY": "+5.00000000E+01"
            }
        }
        self.map_commands = dict(
            MEAS='MEASURE', MEASURE='MEASURE',
            TEMP='TEMPERATURE', TEMPERATURE='TEMPERATURE',
            RH='RHUMIDITY', RHUMIDITY='RHUMIDITY',
            ROUT='ROUTE', ROUTE='ROUTE',
            OPEN='OPEN',
            CLOS='CLOSE', CLOSE='CLOSE',
        )

    def clear_status(self, params, isQuery):
        return

    def reset(self, params, isQuery):
        return

    def is_valid_route(self, route: int):
        route_str = str(route)
        if len(route_str) != 3:
            return False
        p = int(route_str[0])
        c = int(route_str[1:3])
        num_slots = self.num_slots
        num_channels = self.num_channels
        is_valid = (p > 0) and (p <= num_slots) and (c > 0) and (c <= num_channels)
        return is_valid

    def set_channel(self, route: int, closed: bool):
        if not self.is_valid_route(route):
            return
        if closed:
            src_list = self.state["ROUTE"]["OPEN"]
            dst_list = self.state["ROUTE"]["CLOSE"]
        else:
            src_list = self.state["ROUTE"]["CLOSE"]
            dst_list = self.state["ROUTE"]["OPEN"]
        if route in src_list:
            dst_list.append(route)
            del src_list[src_list.index(route)]

    def process_command(self, cmd_tree, params, is_query):
        rst: Union[str, int, float, callable, Dict, List] = self.state
        prst = None
        pcmd = None
        for cmd in cmd_tree:
            mapped_cmd = self.map_commands.get(cmd, cmd)
            if mapped_cmd in rst:
                prst = rst  # noqa
                pcmd = mapped_cmd
                rst = rst[mapped_cmd]
            else:
                break
        if is_query:
            # For rout:open? @() and rout:clos? @()
            if type(rst) == list and len(params):
                route_str = re.sub(r"[@\(\)]", "", params[0]).strip()
                route_names = route_str.split(",")
                if len(route_names) is 1:
                    reply = "1" if int(route_names[0]) in rst else "0"
                else:
                    reply = ','.join(["1" if r in rst else "0" for r in route_names])
                return reply
            elif type(rst) in [str, int, float, bool]:
                return str(rst)
            elif callable(rst):
                return rst(params, True)  # type: ignore
            else:
                return '-100'
        else:
            # For rout:open @() and rout:clos? @()
            if type(rst) is list and len(params):
                route_str = re.sub(r"[@\(\)]", "", params[0]).strip()
                route_names = route_str.split(",")
                closed = (pcmd == "CLOSE")
                for route in route_names:
                    self.set_channel(int(route), closed)
                return None
            elif callable(rst):
                return rst(params, False)  # type: ignore
            else:
                raise Exception('Unknown command')
