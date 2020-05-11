# pylint: skip-file
import socket
import re
import threading
import logging


class DummyTCPInstrument(threading.Thread):
    def __init__(self, bus_address, buffer_size=1024, *args, **kwargs):
        super(DummyTCPInstrument, self).__init__()
        self.logger = logging.getLogger(__name__)
        if bus_address.startswith('TCPIP::'):
            address_components = bus_address.split('::')
            self.tcp_address = address_components[1]
            self.tcp_port = int(address_components[2])
        else:
            address_components = bus_address.split(':')
            self.tcp_address = address_components[0]
            self.tcp_port = int(address_components[1])
        self.buffer_size = buffer_size
        self.tcp_socket = None
        self.connected = False
        self.conn = None
        self.prior_data = ''
        self.read_term = '\n'
        self.write_term = '\n'
        print(self.tcp_address, self.tcp_port)

    def open(self, read_term='\n', write_term='\n', baud_rate=None):
        self.shutdown = False
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind((self.tcp_address, self.tcp_port))
        self.tcp_socket.listen(1)
        self.read_term = read_term
        self.write_term = write_term
        self.baud_rate = baud_rate

    def close(self):
        if self.conn:
            self.conn.close()
            self.tcp_socket.close()
        self.tcp_socket = None
        self.prior_data = ''

    def run(self):
        self.conn, addr = self.tcp_socket.accept()
        self.logger.debug('Connection address: {0}'.format(addr))
        self.connected = True
        while self.connected:
            try:
                data = self.conn.recv(self.buffer_size)
                if data:
                    self.process_packet(self.conn, data)
                else:
                    self.logger.debug('Disconnected from address: {0}'.format(addr))
                    self.connected = False
            except Exception:
                self.logger.debug('Disconnected from address: {0}'.format(addr))
                self.connected = False
        self.conn.close()

    def extract_commands(self, bin_data):
        data = self.prior_data + bin_data.decode()
        self.prior_data = ''
        data = str(data.replace('\r', ''))
        cmds = re.split(';|{0}'.format(self.write_term), data)
        cmds = list(filter(None, cmds))
        if data[-1] != self.write_term:
            self.prior_data = cmds[-1]
            del cmds[-1]
        return cmds

    def process_packet(self, conn, bin_data):
        cmds = self.extract_commands(bin_data)
        for cmd in cmds:
            cmd = cmd.rstrip().upper()
            cmd_parts = cmd.split(' ')
            cmd_name = cmd_parts[0]
            cmd_tree = cmd_name.split(':')
            cmd_params = cmd_parts[1:] if len(cmd_parts) > 1 else []
            is_query = cmd_tree[-1][-1] is '?'
            if is_query:
                cmd_tree[-1] = cmd_tree[-1].rstrip('?')
            self.logger.debug('RECV CMD: {0}\n'.format(cmd))
            try:
                reply = self.process_command(cmd_tree, cmd_params, is_query)
                if is_query and reply is not None:
                    reply += self.read_term
                    rdata = reply.encode()
                    self.logger.debug('SENT CMD: {0}'.format(rdata[:80]))  # First 80 chars
                    conn.sendall(rdata)
            except Exception as err:
                self.logger.error(err)
                # raise err

    def process_command(self, cmd_tree, params, is_query):
        return None
