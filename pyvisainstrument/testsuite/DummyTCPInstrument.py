# pylint: skip-file

import socket
import re


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
                print("SENT CMD: {}".format(rdata[:80]))  # First 80 chars
                conn.sendall(rdata)

    def processCommand(self, cmdTree, params, isQuery):
        return None
