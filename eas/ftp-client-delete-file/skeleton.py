import json
import socket
import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch


class FTPClient:
    def __init__(self, host='127.0.0.1', port=2000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.sock.connect((self.host, self.port))
        return self.sock.recv(1024)

    def send_command(self, command):
        if command.startswith("DELE"):
            cmd, filename = command.split(" ")
            message = {
                "command": cmd,
                "filename": filename
            }
            self.sock.sendall((json.dumps(message) + "\r\n").encode())            
        else: 
            self.sock.sendall((command + "\r\n").encode())
        
        resp = self.sock.recv(1024)
        print(resp.decode())

    def login(self, username, password):
        self.send_command(f"USER {username}")
        self.send_command(f"PASS {password}")

    def delete_file(self, filename):
        self.send_command(f"DELE {filename}")

    def quit(self):
        self.send_command("QUIT")

    def close(self):
        self.sock.close()

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

class TestFTPClient(unittest.TestCase):

    @patch('socket.socket')
    def test_connect(self, mock_socket):
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.recv.return_value = b'220 Welcome to the FTP server\r\n'

        client = FTPClient()
        client.connect()
        
        mock_sock_instance.connect.assert_called_once_with(('127.0.0.1', 2000))
        print(f"connect called with {mock_sock_instance.connect.call_args}") 
        mock_sock_instance.recv.assert_called_once_with(1024)
        print(f"recv called with {mock_sock_instance.recv.call_args}")

    @patch('socket.socket')
    def test_send_command(self, mock_socket):
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.recv.return_value = b'331 Username OK, need password\r\n'

        client = FTPClient()
        client.connect()
        client.send_command("USER test")

        mock_sock_instance.sendall.assert_called_once_with(b'USER test\r\n')
        print(f"sendall called with {mock_sock_instance.sendall.call_args}")
        mock_sock_instance.recv.assert_called_with(1024)

    @patch('socket.socket')
    def test_delete_file(self, mock_socket):
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.recv.return_value = b'250 File deleted successfully\r\n'

        client = FTPClient()
        client.connect()
        client.delete_file("testfile.txt")

        command = json.dumps({"command": "DELE", "filename": "testfile.txt"}) + "\r\n"
        mock_sock_instance.sendall.assert_called_once_with(command.encode('utf-8'))
        print(f"sendall called with {mock_sock_instance.sendall.call_args}")
        mock_sock_instance.recv.assert_called_with(1024)

    @patch('socket.socket')
    def test_quit(self, mock_socket):
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.recv.return_value = b'221 Goodbye\r\n'

        client = FTPClient()
        client.connect()
        client.quit()

        mock_sock_instance.sendall.assert_called_once_with(b'QUIT\r\n')
        print(f"sendall called with {mock_sock_instance.sendall.call_args}")
        mock_sock_instance.recv.assert_called_with(1024)

    @patch('socket.socket')
    def test_close(self, mock_socket):
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance

        client = FTPClient()
        client.connect()
        client.close()

        mock_sock_instance.close.assert_called_once()

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        ftp_client = FTPClient()
        ftp_client.connect()
        ftp_client.login("user", "pass")
        ftp_client.delete_file("testfile.txt")
        ftp_client.quit()
        ftp_client.close()
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
