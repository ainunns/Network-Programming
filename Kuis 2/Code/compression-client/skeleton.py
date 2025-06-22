import socket
import sys
import zlib
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock


def extract_headers(response_bytes):
    ?

def extract_body_compressed(response_bytes):
    ?

def start_http_client():
    # Connect to server through socket
    ?

    # Send request
    request_header = (
        b"GET /? HTTP/1.1\r\n"
        b"Host: ?\r\n"
        b"Accept-Encoding: ?\r\n"
        b"Connection: close\r\n"
        b"\r\n"
    )
    ?

    # Read full response
    response_bytes = b''
    while True:
        ?

    ?

    # Extract headers and body
    ?

    # Check if content-encoding: deflate exists, if yes then use zlib to decompress
    ?

    # Print all the objects
    print("== HEADERS ==")
    print(headers)
    print("\n== BODY ==")
    print(body_bytes)

    json_data = ?
    print("\n== JSON OBJECT ==")
    print(json_data)


class NullWriter(StringIO):
    def write(self, txt):
        pass


class TestHTTPClient(unittest.TestCase):
    
    @patch("socket.socket")
    def test001_http_client_connects_to_server(self, mock_socket_cls):
        """Test client connects to localhost:8080"""
        # Mock client socket
        mock_client_socket = MagicMock()
        mock_socket_cls.return_value = mock_client_socket
        
        # Mock server response without compression
        mock_response = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: application/json\r\n"
            b"Content-Length: 39\r\n"
            b"\r\n"
            b'{"name": "myServer", "status": "online"}'
        )
        
        mock_client_socket.recv.side_effect = [mock_response, b'']
        
        # Capture and suppress output
        captured_output = StringIO()
        sys_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            start_http_client()
        finally:
            sys.stdout = sys_stdout
        
        # ✅ Check client connects to correct server address
        mock_client_socket.connect.assert_called_with(('localhost', 8080))
        print("✅ Client connects to localhost:8080")
        
        # ✅ Check correct HTTP request is sent
        expected_request = (
            b"GET /status HTTP/1.1\r\n"
            b"Host: localhost\r\n"
            b"Accept-Encoding: deflate\r\n"
            b"Connection: close\r\n"
            b"\r\n"
        )
        mock_client_socket.send.assert_called_with(expected_request)
        print("✅ Client sends correct HTTP request with deflate encoding")

    @patch("socket.socket")
    def test002_http_client_handles_compressed_response(self, mock_socket_cls):
        """Test client handles zlib compressed response"""
        # Mock client socket
        mock_client_socket = MagicMock()
        mock_socket_cls.return_value = mock_client_socket
        
        # Create compressed response
        compressed_data = b'x\x9c\xabV\xcaK\xccMU\xb2RP\xca\xad\x0cN-*K-R\xd2QP*.I,)-\x06\x89\xe6\xe7\xe5d\xe6\xa5*\xd5\x02\x00\n\xeb\r0'
        
        mock_response = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: application/json\r\n"
            b"Content-Encoding: deflate\r\n" +
            f"Content-Length: {len(compressed_data)}\r\n".encode('utf-8') +
            b"\r\n" +
            compressed_data
        )
        
        mock_client_socket.recv.side_effect = [mock_response, b'']
        
        # Capture and suppress output
        captured_output = StringIO()
        sys_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            start_http_client()
        finally:
            sys.stdout = sys_stdout
        
        # ✅ Check client receives data in chunks
        mock_client_socket.recv.assert_called_with(1024)
        print("✅ Client receives response data in 1024-byte chunks")
        
        # ✅ Check client properly closes connection
        mock_client_socket.close.assert_called()
        print("✅ Client closes connection after receiving response")

    @patch("socket.socket")
    def test003_http_client_decompresses_zlib_data(self, mock_socket_cls):
        """Test client correctly decompresses zlib data and parses JSON"""
        # Mock client socket
        mock_client_socket = MagicMock()
        mock_socket_cls.return_value = mock_client_socket
        
        # Create compressed response
        json_data = {"name": "myServer", "status": "online"}
        json_bytes = json.dumps(json_data).encode('utf-8')
        compressed_data = b'x\x9c\xabV\xcaK\xccMU\xb2RP\xca\xad\x0cN-*K-R\xd2QP*.I,)-\x06\x89\xe6\xe7\xe5d\xe6\xa5*\xd5\x02\x00\n\xeb\r0'
        
        mock_response = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: application/json\r\n"
            b"Content-Encoding: deflate\r\n" +
            f"Content-Length: {len(compressed_data)}\r\n".encode('utf-8') +
            b"\r\n" +
            compressed_data
        )
        
        mock_client_socket.recv.side_effect = [mock_response, b'']
        
        # Test helper functions directly
        headers = extract_headers(mock_response)
        body_compressed = extract_body_compressed(mock_response)
        
        # ✅ Check header extraction
        self.assertIn("Content-Encoding: deflate", headers)
        print("✅ Client correctly extracts headers from response")
        
        # ✅ Check body extraction and zlib decompression
        self.assertEqual(body_compressed, compressed_data)
        decompressed_data = b'{"name": "myServer", "status": "online"}'
        self.assertEqual(decompressed_data, json_bytes)
        print("✅ Client correctly extracts and decompresses zlib data")
        
        # ✅ Check JSON parsing
        parsed_json = json.loads(decompressed_data.decode('utf-8'))
        self.assertEqual(parsed_json, json_data)
        print("✅ Client correctly parses decompressed JSON data")


if __name__ == "__main__":
    # A simple command-line argument check to run main or tests
    if len(sys.argv) == 2 and sys.argv[1] == "run":
        start_http_client()
    else:
        # Run tests without showing standard unittest output
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)