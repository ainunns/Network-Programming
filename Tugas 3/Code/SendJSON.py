import socket
from io import StringIO
import json
import sys
import unittest
from unittest.mock import MagicMock, patch

host = 'httpbin.org'

def post_data(data):
    json_data = json.dumps(data)

    headers = {
        "Host": host,
        "Content-Type": "application/json",
        "Content-Length": len(json_data),
        "Connection": "close",
    }

    request = "POST /post HTTP/1.1\r\n"
    for header, value in headers.items():
        request += f"{header}: {value}\r\n"
    request += "\r\n"
    request += json_data

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, 80))
        sock.send(request.encode('utf-8'))

        response = sock.recv(1024)

    response_parts = response.split(b'\r\n\r\n', 1)
    headers = response_parts[0].decode('utf-8')
    body = response_parts[1].decode('utf-8')

    return body


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')


class TestPostData(unittest.TestCase):
    @patch('socket.socket')
    def test_post_data(self, mock_socket):
        # Setup the mocked socket instance
        mock_sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_instance

        # Define the mock response from the server
        response_body = {"received": "ok", "status": "success"}
        http_response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Length: {}\r\n"
            "\r\n"
            "{}".format(len(json.dumps(response_body)), json.dumps(response_body))
        )
        mock_sock_instance.recv.side_effect = [http_response.encode('utf-8'), b'']

        # Call the function
        data = {"name": "John Doe", "age": 30}
        body = post_data(data)

        # Assertions to check if the response body is correctly returned
        mock_sock_instance.connect.assert_called_once_with(('httpbin.org', 80))
        print(f"connect called with: {mock_sock_instance.connect.call_args}")

        mock_sock_instance.send.assert_called_once()
        print(f"send called with: {mock_sock_instance.send.call_args}")

        mock_sock_instance.recv.assert_called()
        print(f"recv called with: {mock_sock_instance.recv.call_args}")

        assert_equal(body, json.dumps(response_body))


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        data = {"name": "John Doe", "age": 30}
        return_data = post_data(data)
        print(return_data)

    # run unit test to test locally
    # or for domjudge
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)
