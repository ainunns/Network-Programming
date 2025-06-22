import hashlib
import socket
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

# Client functionality using UDP
def client_program():
    host = '127.0.0.1'
    port = 12345
    message = b'Hello, Server! Please hash this message.'

    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send the message to the server
    client_socket.sendto(message, (host, port))

    # Receive the hash from the server
    hash_response, _ = client_socket.recvfrom(1024)

    # Print the original message and the received hash
    print(f"Original message: {message.decode()}")
    print(f"Received hash: {hash_response.decode()}")

    # close the socket
    client_socket.close()

# Unit test for the UDP client code
class TestClient(unittest.TestCase):
    @patch('socket.socket')  # Mock the socket object
    def test_client_program(self, mock_socket):
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        test_message = "Hello, Server! Please hash this message."
        expected_hash = hashlib.md5(test_message.encode()).hexdigest()
        mock_socket_instance.recvfrom.return_value = (expected_hash.encode(), ('127.0.0.1', 12345))

        # Run the client program
        client_program()

        # Verify the client sends the correct message to the correct address
        mock_socket_instance.sendto.assert_called_with(test_message.encode(), ('127.0.0.1', 12345))
        print(f"sendto called with: {mock_socket_instance.sendto.call_args}")

        # Verify the client receives a response
        mock_socket_instance.recvfrom.assert_called_with(1024)
        print(f"recvfrom called with: {mock_socket_instance.recvfrom.call_args}")

        # Verify the client closes the socket after receiving the hash
        mock_socket_instance.close.assert_called_once()
        print(f"close called with: {mock_socket_instance.close.call_args}")

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

if __name__ == '__main__':
    # Run unittest with a custom runner that suppresses output
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)

    # Uncomment this if you want to run the client program manually
    # client_program()
