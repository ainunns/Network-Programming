import select
import socket
import os
import sys
import unittest
import zlib
from io import StringIO
from unittest.mock import call, patch, Mock


def handle_client(client_socket):
    # Send the welcome message
    client_socket.sendall("220 Welcome to Simple SMTP Server\r\n")
    
    # Receive and process commands
    while True:
        # Receive the command
        data = client_socket.recv(1024).decode("utf-8")
        
        print(f"Received: {data.strip()}")

        # Send the response
        # if data starts with 'EHLO'  send '250 Hello\r\n'
        # etc.
        if data.upper().startswith("EHLO"):
            print("EHLO")
            client_socket.sendall(b"220 Welcome to Simple SMTP Server\r\n")

    # close the socket
    client_socket.close()

def start_smtp_server(address='localhost', port=1025):
    # create a socket, bind it to the address and port, and start listening
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((address, port))
    server_socket.listen(5)
    
    socket_list = [server_socket]
    client_data = {}

    while True:
        # accept a connection
        readable_socket, _, _ = select.select(socket_list, [], [])
        for read_socket in readable_socket:
            if read_socket is server_socket:
                client_socket, client_address = server_socket.accept()
                client_socket.setblocking(False)
                
                socket_list.append(client_socket)
                client_data[client_socket] = b''
                
                print(f"New client connected: {client_address}")
                
                client_socket.sendall("220 Welcome to Simple SMTP Server\r\n")
            else:
                data = read_socket.recv(1024)
                if data:
                    client_data[read_socket] += data
                    if b'\r\n' in client_data[read_socket]:
                        break
                else:
                    inputs.remove(read_socket)
                    del client_data[read_socket]

                read_socket.close()

        # handle the client
        for client in socket_list:
            handle_client(client_socket)

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

class TestSMTPServer(unittest.TestCase):

    @patch('socket.socket')
    def test_handle_client(self, mock_socket):
        # Mock the client socket
        mock_client_socket = Mock()

        # Simulate a sequence of client commands and expected responses
        command_response_pairs = [
            (b'EHLO example.com\r\n', b'250 Hello\r\n'),
            (b'MAIL FROM:<test@example.com>\r\n', b'250 OK\r\n'),
            (b'RCPT TO:<recipient@example.com>\r\n', b'250 OK\r\n'),
            (b'DATA\r\n', b'354 End data with <CR><LF>.<CR><LF>\r\n'),
            (b'.\r\n', b'250 OK: message accepted for delivery\r\n'),
            (b'QUIT\r\n', b'221 Bye\r\n'),
        ]

        # Configure the mock to return each command in sequence when recv is called
        mock_client_socket.recv.side_effect = [command for command, _ in command_response_pairs] + [b'']

        # Call the handle_client function with the mock socket
        handle_client(mock_client_socket)

        # Check that send was called with the expected responses
        expected_calls = [call(response) for _, response in command_response_pairs]
        mock_client_socket.send.assert_has_calls(expected_calls, any_order=False)
        print(f"sending calls: {mock_client_socket.send.call_args_list}")

        # Check that the socket was closed
        mock_client_socket.close.assert_called_once()
        print(f"closing calls: {mock_client_socket.close.call_args_list}")

if __name__ == '__main__':
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)
