import hashlib
import socket
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

# Server function using UDP
def handle_client_message(server_socket, data, addr):
    """Handle a single UDP client message."""
    print(f"Received from {addr}: {data.decode()}")

    # Calculate MD5 hash
    hashed_data = hashlib.md5(data).hexdigest().encode('utf-8')

    # Send the hash back to the client
    server_socket.sendto(hashed_data, addr)

def start_server():
    """Start the UDP server and listen for incoming messages."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = '127.0.0.1'
    port = 12345
    
    # bind the socket to the address and port
    server_socket.bind((host, port))
    
    print(f"UDP server listening on {host}:{port} ...")
    try:
        while True:
            # Receive data from clients
            data, addr = server_socket.recvfrom(1024)
            
            # handle the received message
            handle_client_message(server_socket, data, addr)
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        # close the server socket
        server_socket.close()

class ExitLoopException(Exception):
    pass

# 'Null' stream to discard output
class NullWriter(StringIO):
    def write(self, txt):
        pass

# Unit test for UDP server
class TestServer(unittest.TestCase):
    @patch('socket.socket')
    def test_handle_client_message(self, mock_socket):
        print('Test handle_client_message ...')
        mock_server_socket = MagicMock()
        mock_addr = ('127.0.0.1', 54321)
        test_message = b"Hello, Server! Please hash this message."
        expected_hash = hashlib.md5(test_message).hexdigest()

        # Call the function directly with mocked data
        handle_client_message(mock_server_socket, test_message, mock_addr)

        # Verify the server sent the correct hash to the client
        mock_server_socket.sendto.assert_called_with(expected_hash.encode(), mock_addr)
        print(f"sendto called with: {mock_server_socket.sendto.call_args}")

    @patch('socket.socket')
    def test_start_server(self, mock_socket):
        print('Test start_server ...')
        mock_server_socket = MagicMock()
        test_message = b"Test message for start_server"
        mock_addr = ('127.0.0.1', 54321)

        mock_socket.return_value = mock_server_socket
        mock_server_socket.recvfrom.side_effect = [(test_message, mock_addr), ExitLoopException]

        try:
            start_server()
        except ExitLoopException:
            pass  # used to break the infinite loop

        mock_server_socket.bind.assert_called_once_with(('127.0.0.1', 12345))
        print(f"bind called with: {mock_server_socket.bind.call_args}")
        mock_server_socket.recvfrom.assert_called()
        print(f"recvfrom called with: {mock_server_socket.recvfrom.call_args}")

if __name__ == '__main__':
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)

    # Uncomment this to run the actual server
    # start_server()
