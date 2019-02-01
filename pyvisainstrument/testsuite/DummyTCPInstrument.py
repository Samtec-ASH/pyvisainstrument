# pylint: skip-file
import socket
import re
import threading
import logging


class DummyTCPInstrument(threading.Thread):
    def __init__(self, busAddress, bufferSize=1024, *args, **kwargs):
        super(DummyTCPInstrument, self).__init__()
        self.logger = logging.getLogger(__name__)
        if busAddress.startswith('TCPIP::'):
            addressComponents = busAddress.split('::')
            self.tcpAddress = addressComponents[1]
            self.tcpPort = int(addressComponents[2])
        else:
            addressComponents = busAddress.split(':')
            self.tcpAddress = addressComponents[0]
            self.tcpPort = int(addressComponents[1])
        self.bufferSize = bufferSize
        self.tcpSocket = None
        self.connected = False
        self.conn = None
        self.priorData = ''
        self.readTerm = '\n'
        self.writeTerm = '\n'
        print(self.tcpAddress, self.tcpPort)

    def open(self, readTerm='\n', writeTerm='\n', baudRate=None):
        self.shutdown = False
        self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcpSocket.bind((self.tcpAddress, self.tcpPort))
        self.tcpSocket.listen(1)
        self.readTerm = readTerm
        self.writeTerm = writeTerm
        self.baudRate = baudRate

    def close(self):
        if self.conn:
            self.conn.close()
            self.tcpSocket.close()
        self.tcpSocket = None
        self.priorData = ''

    def run(self):
        self.conn, addr = self.tcpSocket.accept()
        self.logger.debug('Connection address: {0}'.format(addr))
        self.connected = True
        while self.connected:
            try:
                data = self.conn.recv(self.bufferSize)
                if data:
                    self.processPacket(self.conn, data)
                else:
                    self.logger.debug('Disconnected from address: {0}'.format(addr))
                    self.connected = False
            except Exception:
                self.logger.debug('Disconnected from address: {0}'.format(addr))
                self.connected = False
        self.conn.close()

    def extractCommands(self, binData):
        data = self.priorData + binData.decode()
        self.priorData = ''
        data = str(data.replace('\r', ''))
        cmds = re.split(';|{0}'.format(self.writeTerm), data)
        cmds = list(filter(None, cmds))
        if data[-1] != self.writeTerm:
            self.priorData = cmds[-1]
            del cmds[-1]
        return cmds

    def processPacket(self, conn, binData):
        cmds = self.extractCommands(binData)
        for cmd in cmds:
            cmd = cmd.rstrip().upper()
            cmdParts = cmd.split(' ')
            cmdName = cmdParts[0]
            cmdTree = cmdName.split(':')
            cmdParams = cmdParts[1:] if len(cmdParts) > 1 else []
            isQuery = cmdTree[-1][-1] is '?'
            if isQuery:
                cmdTree[-1] = cmdTree[-1].rstrip('?')
            self.logger.debug('RECV CMD: {0}\n'.format(cmd))
            try:
                reply = self.processCommand(cmdTree, cmdParams, isQuery)
                if reply is not None:
                    reply += self.readTerm
                    rdata = reply.encode()
                    self.logger.debug('SENT CMD: {0}'.format(rdata[:80]))  # First 80 chars
                    conn.sendall(rdata)
            except Exception as err:
                self.logger.error(err)

    def processCommand(self, cmdTree, params, isQuery):
        return None
