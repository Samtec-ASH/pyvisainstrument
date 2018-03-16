
# pylint: skip-file

import re
from pyvisainstrument.testsuite.DummyTCPInstrument import DummyTCPInstrument


class DummyDAQ(DummyTCPInstrument):

    def __init__(self, numPorts, numChannels, *args, **kwargs):
        super(DummyDAQ, self).__init__(*args, **kwargs)
        self.params = dict(numPorts=numPorts, numChannels=numChannels)
        self.state = {
            "*CLS": self.clearStatus,
            "*RST": self.reset,
            "*IDN": "34970A",
            "*OPC": "1",
            "*ESR": "1",
            "ROUTE": {
                "OPEN": [str.format("{:01d}{:02d}", p+1, c+1) for p in range(numPorts) for c in range(numChannels)],
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
        numPorts = self.params["numPorts"]
        numChannels = self.params["numChannels"]
        isValid = (p > 0) and (p <= numPorts) and (c > 0) and (c <= numChannels)
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
                print("Unknown query")
                return str("-100")
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
                print("Unknown command")
                return None


def runDummyDAQ():
    try:
        TCP_IP = '127.0.0.1'
        TCP_PORT = 5021
        baseArgs = dict(tcpAddress=TCP_IP, tcpPort=TCP_PORT, termStr='\n', bufferSize=1024)
        instr = DummyDAQ(numPorts=3, numChannels=20, **baseArgs)
        instr.open()
        instr.run()
    except:
        pass
    finally:
        instr.close()


if __name__ == "__main__":
    runDummyDAQ()
