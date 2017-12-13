import socket
import re
import threading
import numpy as np


class DummyTCPInstrument(object):
    def __init__(self, tcpAddress, tcpPort, termStr='\n', bufferSize=1024):
        self.tcpAddress = tcpAddress
        self.tcpPort = tcpPort
        self.termStr = termStr
        self.bufferSize = bufferSize
        self.tcpSocket = None
        self.connected = False
        self.priorData = str("")

    def open(self):
        self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcpSocket.bind((self.tcpAddress, self.tcpPort))
        self.tcpSocket.listen(1)

    def close(self):
        self.tcpSocket.close()

    def run(self):
        conn, addr = self.tcpSocket.accept()
        print("Connection address: {}".format(addr))
        self.connected = True
        while self.connected:
            data = conn.recv(self.bufferSize)
            if data:
                #print("received data: {}".format(data))
                self.processPacket(conn, data)
            else:
                print("Disconnected from address: {}".format(addr))
                self.connected = False
        conn.close()

    def extractCommands(self, binData):
        data = self.priorData + binData.decode()
        self.priorData = str("")
        data = str(data.replace('\r', ''))
        cmds = re.split(';|\n', data)
        cmds = list(filter(None, cmds))
        if data[-1] is not '\n':
            self.priorData = cmds[-1]
            del cmds[-1]
        return cmds

    def processPacket(self, conn, binData):
        cmds = self.extractCommands(binData)
        for cmd in cmds:
            cmd = cmd.rstrip().upper()
            cmdParts = cmd.split(" ")
            cmdName = cmdParts[0]
            cmdTree = cmdName.split(":")
            cmdParams = cmdParts[1:] if len(cmdParts) > 1 else []
            isQuery = cmdTree[-1][-1] is "?"
            if isQuery:
                cmdTree[-1] = cmdTree[-1].rstrip("?")
            print("RECV CMD: {}\n".format(cmd))
            reply = self.processCommand(cmdTree, cmdParams, isQuery)
            if reply is not None:
                reply += self.termStr
                rdata = reply.encode()
                print("SENT CMD: {}".format(rdata[:80])) #  First 80 chars
                conn.sendall(rdata)

    def processCommand(self, cmdTree, params, isQuery):
        return None


class DummyDAQ(DummyTCPInstrument):

    def __init__(self, numPorts, numChannels, *args, **kwargs):
        super(DummyDAQ, self).__init__(*args, **kwargs)
        self.params = dict(numPorts=numPorts, numChannels=numChannels)
        self.state = {
            "*IDN": "DAQ",
            "*OPC": "1",
            "ROUT": {
                "OPEN": [str.format("{:01d}{:02d}", p+1, c+1) for p in range(numPorts) for c in range(numChannels)],
                "CLOS": [],
                "DONE": "1"
            }
        }

    def isValidRoute(self, route):
        if len(route) != 3:
            return False
        p = int(route[0])
        c = int(route[1:3])
        numPorts = self.params["numPorts"]
        numChannels = self.params["numChannels"]
        isValid = (p > 0) and (p <= numPorts) and (c > 0) and (c <= numChannels)
        return isValid

    def _setChannel(self, route, asClosed):
        if not self.isValidRoute(route):
            return
        if asClosed:
            srcList = self.state["ROUT"]["OPEN"]
            dstList = self.state["ROUT"]["CLOS"]
        else:
            srcList = self.state["ROUT"]["CLOS"]
            dstList = self.state["ROUT"]["OPEN"]
        if route in srcList:
            dstList.append(route)
            del srcList[srcList.index(route)]

    def processCommand(self, cmdTree, params, isQuery):
        rst = self.state
        prst = None
        pcmd = None
        for cmd in cmdTree:
            if cmd in rst:
                prst = rst
                pcmd = cmd
                rst = rst[cmd]
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
            else:
                print("Unknown query")
                return str("-100")
        else:
            # For rout:open @() and rout:clos? @()
            if type(rst) is list and len(params):
                routeStr = re.sub("[@\(\)]", "", params[0]).strip()
                routeNames = routeStr.split(",")
                asClosed = (pcmd == "CLOS")
                print(cmdTree, params, routeNames)
                for route in routeNames:
                    self._setChannel(route, asClosed)
                return None
            else:
                print("Unknown command")
                return None


class DummyPS(DummyTCPInstrument):

    def __init__(self, *args, **kwargs):
        super(DummyPS, self).__init__(*args, **kwargs)
        self.MAX_VOLT = 24
        self.MIN_VOLT = 0
        self.MAX_CURR = 5
        self.MIN_CURR = 0
        self.OUTPUT_ID = dict(P6V=1, P25V=2, N25V=3, OUTP1=1, OUTP2=2)
        self.state = {
            1: {
                "MEAS": dict(VOLT=dict(DC=0), CURR=dict(DC=0)),
                "OUTP": dict(STAT="OFF"),
                "VOLT": dict(MIN="0", MAX="24", SET="0"),
                "CURR": dict(MIN="0", MAX="5", SET="5")
            },
            2: {
                "MEAS": dict(VOLT=dict(DC=0), CURR=dict(DC=0)),
                "OUTP": dict(STAT="OFF"),
                "VOLT": dict(MIN="0", MAX="24", SET="0"),
                "CURR": dict(MIN="0", MAX="5", SET="5")
            },
            3: {
                "MEAS": dict(VOLT=dict(DC=0), CURR=dict(DC=0)),
                "OUTP": dict(STAT="OFF"),
                "VOLT": dict(MIN="0", MAX="24", SET="0"),
                "CURR": dict(MIN="0", MAX="5", SET="5")
            },
            "VOLT": self._voltageSetPointHandler,
            "CURR": self._currentLimitHandler,
            ""
            "DISP": dict(TEXT=dict(DATA="", CLEA=None)),
            "INST": dict(NSEL=1, SEL="P6V"),
            "*IDN": "PS",
            "*OPC": "1"
        }

    def _voltageSetPointHandler(self, params, isQuery):
        print(params)
        print(isQuery)
        if isQuery:
            fieldName = params[0] if len(params) else "SET"
            return self.state[int(self._currInst())]["VOLT"][fieldName]
        else:
            self.state[int(self._currInst())]["VOLT"]["SET"] = params[0]
            self.state[int(self._currInst())]["MEAS"]["VOLT"]["DC"] = params[0]
            return None

    def _currentLimitHandler(self, params, isQuery):
        if isQuery:
            fieldName = params[0] if len(params) else "SET"
            return self.state[int(self._currInst())]["CURR"][fieldName]
        else:
            self.state[int(self._currInst())]["CURR"]["SET"] = params[0]
            return None

    def _currInst(self):
        return self.state["INST"]["NSEL"]

    def processCommand(self, cmdTree, params, isQuery):
        if cmdTree[0] in ["MEAS", "OUTP"]:
            rst = self.state[self._currInst()]
        else:
            rst = self.state
        prst = None
        pcmd = None
        for cmd in cmdTree:
            if cmd in rst:
                prst = rst
                pcmd = cmd
                rst = rst[cmd]
            else:
                break
        if isQuery:
            if callable(rst):
                return rst(params, isQuery)
            elif type(rst) == dict and len(params):
                return rst.get(params[0], "-100")
            elif type(rst) in [str, int, float, bool]:
                return str(rst)
            else:
                print("Unknown query")
                return str("-100")
        else:
            if callable(rst):
                return rst(params, isQuery)
            if type(prst) is dict and type(rst) in [str, int, float, bool]:
                print(cmdTree, params)
                if len(params):
                    castType = type(params[0]) if rst is None else type(prst[pcmd])
                    prst[pcmd] = castType(params[0])
                return None
            else:
                print("Unknown command")
                return None


class DummyVNA(DummyTCPInstrument):

    def __init__(self, *args, **kwargs):
        super(DummyVNA, self).__init__(*args, **kwargs)
        self.state = {
            "*IDN": "VNA",
            "*OPC": "1",
            "SENSE": {
                "FREQU": {
                    "START": "1E7",
                    "STOP": "1E9",
                    "CENT": "5E8",
                    "CW": "5E8"
                },
                "SWEEP": {
                    "POINT": "100",
                    "STEP": "100",
                    "TYPE": "LINEAR",
                    "POWE": "10",
                    "MODE": "SINGLE"
                },
                "CORR": {
                    "CSET": {"ACT": ""},
                    "COLL": {
                        "GUID": {
                            "STEPS": "3",
                            "DESC": "Please do blah for step blah",
                            "CONN": {
                                "PORT1": None,
                                "PORT2": None,
                                "PORT3": None,
                                "PORT4": None
                            },
                            "CKIT": {
                                "PORT1": None,
                                "PORT2": None,
                                "PORT3": None,
                                "PORT4": None
                            },
                            "ACQ": None,
                            "SAVE": None,
                            "THRU": {"PORTS": None},
                            "INIT": None
                        }
                    },
                    "PREF": {"ECAL": {"ORI": None}}
                }
            },
            "CALC1": {
                "PAR": {
                    "DEL": {"ALL": None},
                    "DEF": "'sdd11',S11",
                    "SEL": "'sdd11'",
                },
                "FSIM": {
                    "BAL": {
                        "DEV": None,
                        "TOP": {"BBAL": {"PPOR": "1,2,3,4"}},
                        "PAR": {"STAT": "ON", "BBAL": {"DEF": "SDD11"}}
                    }
                },
                "DATA": self._getData
            },
            "DISP": {
                "WIND1": {
                    "TRAC1": {"FEED": "sdd11"},
                    "TRAC2": {"FEED": "sdd12"},
                    "TRAC3": {"FEED": "sdd21"},
                    "TRAC4": {"FEED": "sdd22"}
                }
            },
            "TRIG": {
                "SOUR": "IMMediate"
            }
        }

    def _getData(self, params):
        isComplex = len(params) and (params[0] in ["RDATA", "SDATA"])
        numPoints = int(self.state["SENSE"]["SWEEP"]["POINT"])
        if isComplex:
            numPoints = 2*numPoints
        data = np.random.rand(numPoints)
        dataStr = ",".join('{:+.6E}'.format(v) for v in data)
        return dataStr

    def processCommand(self, cmdTree, params, isQuery):
        rst = self.state
        prst = None
        pcmd = None
        for cmd in cmdTree:
            scmd = cmd[:5]
            if scmd in rst:
                prst = rst
                pcmd = scmd
                rst = rst[scmd]
            else:
                break

        if isQuery:
            if type(rst) in [str, int, float, bool]:
                return str(rst)
            elif type(rst) is None:
                return str("")
            elif callable(rst):
                print("calling", rst)
                return rst(params)
            else:
                print("Unknown query")
                return str("-100")
        else:
            if type(prst) is dict and (type(rst) in [str, int, float, bool] or rst is None):
                if len(params):
                    castType = type(params[0]) if rst is None else type(prst[pcmd])
                    prst[pcmd] = castType(params[0])
                return None
            else:
                print("Unknown command", prst, pcmd, rst)
                return None


def runDummyVNA():
    try:
        TCP_IP = '127.0.0.1'
        TCP_PORT = 5020
        baseArgs = dict(tcpAddress=TCP_IP, tcpPort=TCP_PORT, termStr='\n', bufferSize=1024)
        instr = DummyVNA(**baseArgs)
        instr.open()
        instr.run()
    except:
        pass
    finally:
        instr.close()


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


def runDummyPS():
    try:
        TCP_IP = '127.0.0.1'
        TCP_PORT = 5022
        baseArgs = dict(tcpAddress=TCP_IP, tcpPort=TCP_PORT, termStr='\n', bufferSize=1024)
        instr = DummyPS(**baseArgs)
        instr.open()
        instr.run()
    except:
        pass
    finally:
        instr.close()


def runDummyInstruments():
    try:
        while True:
            print("Instruments Opened")
            vnaThread = threading.Thread(target=runDummyVNA, name="VNA")
            daqThread = threading.Thread(target=runDummyDAQ, name="DAQ")
            psThread = threading.Thread(target=runDummyPS, name="PS")
            vnaThread.daemon = True
            daqThread.daemon = True
            psThread.daemon = True
            vnaThread.start()
            daqThread.start()
            psThread.start()
            vnaThread.join()
            daqThread.join()
            psThread.join()
            print("Instruments Closed")
    except KeyboardInterrupt:
        pass
    finally:
        print("Exiting...")


if __name__ == "__main__":
    runDummyInstruments()
