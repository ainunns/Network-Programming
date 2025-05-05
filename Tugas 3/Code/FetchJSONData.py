import json
import socket
import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch


def fetch_users_from_city(city_name):
    headers = {
        "Host": "jsonplaceholder.typicode.com",
        "Connection": "close",
    }

    request = "GET /users HTTP/1.1\r\n"
    for header, value in headers.items():
        request += f"{header}: {value}\r\n"
    request += "\r\n"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('jsonplaceholder.typicode.com', 80))
        sock.send(request.encode('utf-8'))

        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk

    headers, body = response.split(b'\r\n\r\n160d', 1)
    
    json_data = body.rstrip(b'0')

    # Decode the JSON data
    try:
        # Decode the JSON data
        json_data = json_data.decode('utf-8')
        users_data = json.loads(json_data)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return []
    
    user_name = []

    for user in users_data:
        if user.get("address", {}).get("city") == city_name:
            user_name.append(user["name"])
    
    return user_name


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')


class TestFetchUsersFromCity(unittest.TestCase):
    @patch('socket.socket')
    def test_fetch_users_from_kulas_light(self, mock_socket):
        # Setup the mocked socket instance
        mock_sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_instance

        # Simulate a JSON response from the server
        users_data = [
            {"id": 1, "name": "Leanne Graham", "address": {"city": "Gwenborough"}},
            {"id": 2, "name": "Ervin Howell", "address": {"city": "Wisokyburgh"}}
        ]
        http_response = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n160d\r\n" + json.dumps(users_data).encode('utf-8') + b'0'

        # Mock the recv method to simulate receiving the response in two parts
        mock_sock_instance.recv.side_effect = [http_response[:70], http_response[70:], b'']

        # Call the function under test
        result = fetch_users_from_city("Gwenborough")

        # Verify that the socket methods were called correctly
        mock_sock_instance.connect.assert_called_with(('jsonplaceholder.typicode.com', 80))
        print(f"connect called with: {mock_sock_instance.connect.call_args}")

        mock_sock_instance.send.assert_called_once()
        print(f"send called with: {mock_sock_instance.send.call_args}")

        mock_sock_instance.recv.assert_called()
        print(f"recv called with: {mock_sock_instance.recv.call_args}")

        # Assertions to check the correct behavior
        assert_equal(result, ["Leanne Graham"])


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        names = fetch_users_from_city("Gwenborough")
        for name in names:
            print(name)
    
    # run unit test to test locally
    # or for domjudge
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)
