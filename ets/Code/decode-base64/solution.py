import base64
import http.client
import json
import sys
import unittest
from io import StringIO
from unittest import mock


def decode_base64():
    # encoded_message: SGlkdXBKb2tvd2lpaQ==
    conn = http.client.HTTPSConnection("httpbin.org")
    conn.request("GET", "/base64/SGlkdXBKb2tvd2lpaQ==")
    
    response = conn.getresponse()
    conn.close()
    
    body = response.read()
    
    return body.decode()

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to *************')  # hide params if is not equal


class TestDecodeBase64(unittest.TestCase):
    @mock.patch('http.client.HTTPSConnection')
    def test_decode_base64_success(self, mock_conn):
        mock_response = mock.Mock()
        mock_response.status = 200

        encoded_expected = "SGlkdXBKb2tvd2lpaQ=="
        base64_bytes = encoded_expected.encode('utf-8')
        text_bytes = base64.b64decode(base64_bytes)
        expected_result = text_bytes.decode('utf-8')

        mock_response.read.return_value = expected_result.encode('utf-8')
        mock_conn.return_value.getresponse.return_value = mock_response

        result = decode_base64()

        mock_conn.assert_called_once_with("httpbin.org")
        print(f"connection called with: {mock_conn.call_args}")

        mock_conn.return_value.request.assert_called_once_with("GET", "/base64/SGlkdXBKb2tvd2lpaQ==")
        print(f"request called with: {mock_conn.return_value.request.call_args}")

        mock_conn.return_value.close.assert_called_once()
        print(f"connection closed: {mock_conn.return_value.close.call_args}")

        assert_equal(result, expected_result)

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        result = decode_base64()
        print(result)

    # run unit test to test locally
    # or for domjudge
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)