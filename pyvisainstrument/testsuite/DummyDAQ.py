# pylint: skip-file
import re
from pyvisainstrument.testsuite.DummyTCPInstrument import DummyTCPInstrument


class DummyDAQ(DummyTCPInstrument):

    def __init__(self, *args, **kwargs):
        super(DummyDAQ, self).__init__(*args, **kwargs)
        self.numSlots = kwargs['numSlots']
        self.numChannels = kwargs['numChannels']
        openState = ['{:01d}{:02d}'.format(p+1, c+1) for p in range(self.numSlots) for c in range(self.numChannels)]
        self.state = {
            "*CLS": self.clearStatus,
            "*RST": self.reset,
            "*IDN": "34970A",
            "*OPC": "1",
            "*ESR": "1",
            "ROUTE": {
                "OPEN": openState,
                "CLOSE": [],
                "DONE": "1"
            }
        }
        self.mapCommands = dict(
            ROUT='ROUTE', ROUTE='ROUTE',
            OPEN='OPEN',
            CLOS='CLOSE', CLOSE='CLOSE',
        )

    def clearStatus(self, params, isQuery):
        return

    def reset(self, params, isQuery):
        return

    def isValidRoute(self, route):
        if len(route) != 3:
            return False
        p = int(route[0])
        c = int(route[1:3])
        numSlots = self.numSlots
        numChannels = self.numChannels
        isValid = (p > 0) and (p <= numSlots) and (c > 0) and (c <= numChannels)
        return isValid

    def setChannel(self, route, asClosed):
        if not self.isValidRoute(route):
            return
        if asClosed:
            srcList = self.state["ROUTE"]["OPEN"]
            dstList = self.state["ROUTE"]["CLOSE"]
        else:
            srcList = self.state["ROUTE"]["CLOSE"]
            dstList = self.state["ROUTE"]["OPEN"]
        if route in srcList:
            dstList.append(route)
            del srcList[srcList.index(route)]

    def processCommand(self, cmdTree, params, isQuery):
        rst = self.state
        prst = None
        pcmd = None
        for cmd in cmdTree:
            mappedCmd = self.mapCommands.get(cmd, cmd)
            if mappedCmd in rst:
                prst = rst  # noqa
                pcmd = mappedCmd
                rst = rst[mappedCmd]
            else:
                break
        if isQuery:
            # For rout:open? @() and rout:clos? @()
            if type(rst) == list and len(params):
                routeStr = re.sub("[@\(\)]", "", params[0]).strip()
                routeNames = routeStr.split(",")
                if len(routeNames) is 1:
                    reply = "1" if routeNames[0] in rst else "0"
                else:
                    reply = ','.join(["1" if r in rst else "0" for r in routeNames])
                return reply
            elif type(rst) in [str, int, float, bool]:
                return str(rst)
            elif callable(rst):
                return rst(params, True)
            else:
                return '-100'
        else:
            # For rout:open @() and rout:clos? @()
            if type(rst) is list and len(params):
                routeStr = re.sub("[@\(\)]", "", params[0]).strip()
                routeNames = routeStr.split(",")
                asClosed = (pcmd == "CLOSE")
                for route in routeNames:
                    self.setChannel(route, asClosed)
                return None
            elif callable(rst):
                return rst(params, False)
            else:
                raise Exception('Unknown command')
