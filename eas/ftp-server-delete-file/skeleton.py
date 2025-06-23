import json
import os
import select
import socket
import sys
import unittest
from io import StringIO
from unittest import mock


class FTPServer:
    def __init__(self, host='127.0.0.1', port=2000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.sock.setblocking(False)
        self.inputs = [self.sock]
        self.client_data = {}
        
        print(f"Listening on {self.host}:{self.port}")

    def start(self):
        while True:
            readable, _, _ = select.select(self.inputs, [], [])
            for s in readable:
                if s is self.sock:
                    client_sock, client_addr = self.sock.accept()
                    client_sock.setblocking(False)
                    
                    self.inputs.append(client_sock)
                    
                    self.client_data[client_sock] = b''
                    
                    client_sock.sendall("welcome")
                else:
                    data = s.recv(1024)
                    if data:
                        self.client_data[s] += data
                        if b'\r\n' in self.client_data[s]:
                            break
                        else:
                            self.inputs.remove(s)
                            del self.client_data[s]
                            s.close()

    def handle_client(self, client_sock):
        data = self.client_data[client_sock].decode().strip()
        self.client_data[client_sock] = b''
        print(f"Received command: {data}")

        if data.upper().startswith('USER'):
            client_sock.sendall(b'331 Username OK, need password\r\n')
        elif data.upper().startswith('PASS'):
            client_sock.sendall(b'230 User logged in\r\n')
        elif data.upper().startswith('DELE'):
            _, filename = data.split(" ")
            os.remove(filename)
            client_sock.sendall(b'250 File deleted successfully\r\n')
        elif data.upper().startswith('QUIT'):
            client_sock.sendall(b'221 Goodbye\r\n')
            self.inputs.remove(client_sock)
            del self.client_data[client_sock]
            client_sock.close()
        else:
            client_sock.sendall(b'502 Command not implemented\r\n')


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


class TestFTPServer(unittest.TestCase):
    def setUp(self):
        self.server = FTPServer()

    def tearDown(self):
        self.server.sock.close()

    def test_handle_client_user(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: b'USER valid_username\r\n'}
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(b'331 Username OK, need password\r\n')

    def test_handle_client_pass(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: b'PASS valid_password\r\n'}
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(b'230 User logged in\r\n')

    def test_handle_client_dele(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: b'DELE testfile.txt\r\n'}
        with mock.patch('os.remove') as mock_remove:
            self.server.handle_client(client_sock)
            mock_remove.assert_called_with('testfile.txt')
            client_sock.sendall.assert_called_with(b'250 File deleted successfully\r\n')

    def test_handle_client_quit(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: b'QUIT\r\n'}
        self.server.inputs.append(client_sock)
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(b'221 Goodbye\r\n')
        self.assertEqual(self.server.inputs, [self.server.sock])
        self.assertNotIn(client_sock, self.server.client_data)
        client_sock.close.assert_called_once()

    def test_handle_client_unknown_command(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: b'UNKNOWN_COMMAND\r\n'}
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(b'502 Command not implemented\r\n')

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        ftp_server = FTPServer()
        ftp_server.start()
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
