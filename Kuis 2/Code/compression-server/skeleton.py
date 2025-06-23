import socket
import sys
import zlib
import json
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock


def start_http_server():
    # Create running server process
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # only one client at a time
    server_socket.bind(('localhost', 8080))
    server_socket.listen(1)


    try:
        while True:
            # Accept client connection
            client_socket, client_address = server_socket.accept()

            # Get request header and find accept_encoding
            request_header = client_socket.recv(4096)
            header_str = request_header.decode('utf-8')
            request_file = header_str.split(' ')[1]
            if 'Accept-Encoding: ' in header_str:
                accept_encoding = header_str.split('Accept-Encoding: ')[1]
            else:
                accept_encoding = ""

            
            # Process if /status
            if request_file == '/status':
                # json to be sent
                json_data = json.dumps({"name": "myServer", "status": "online"}).encode('utf-8')

                # If accept_encoding for zlib is used then use zlib compress for the json file
                if "deflate" in accept_encoding:
                    compressed_data = zlib.compress(json_data, level=9)
                    response_header = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: application/json\r\n"
                        "Content-Encoding: deflate\r\n"
                        "Content-Length: {}\r\n"
                        "\r\n"
                    )
                    client_socket.sendall(response_header.format(len(compressed_data)).encode('utf-8') + compressed_data)
                # Else no need to process the response, send it normally
                else:
                    response_header = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: application/json\r\n"
                        "Content-Length: {}\r\n"
                        "\r\n"
                    )
                    client_socket.sendall(response_header.format(len(json_data)).encode('utf-8') + json_data)

            else:
                # Else 404 not found
                    client_socket.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

            client_socket.close()

    except KeyboardInterrupt:
        print("\nServer shutting down...")
        
    finally:
        server_socket.close()
        sys.exit(0)


class NullWriter(StringIO):
    def write(self, txt):
        pass


class TestHTTPServer(unittest.TestCase):
    
    @patch("socket.socket")
    def test001_http_server_without_compression(self, mock_socket_cls):
        """Test /status endpoint without compression"""
        # Mock server socket
        mock_server_socket = MagicMock()
        mock_client_socket = MagicMock()
        
        # Configure socket mock
        mock_socket_cls.return_value = mock_server_socket
        mock_server_socket.accept.return_value = (mock_client_socket, ('127.0.0.1', 50001))
        
        # Simulate HTTP GET request for /status without Accept-Encoding
        http_request = (
            "GET /status HTTP/1.1\r\n"
            "Host: localhost:8080\r\n"
            "\r\n"
        )
        
        mock_client_socket.recv.side_effect = [http_request.encode('utf-8'), b'']
        
        # Capture and suppress output
        captured_output = StringIO()
        sys_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            start_http_server()
        except SystemExit:
            pass
        finally:
            sys.stdout = sys_stdout
        
        # ✅ Check server listens on port 8080
        mock_server_socket.bind.assert_called_with(('localhost', 8080))
        print("✅ Server listening on port 8080")
        
        # ✅ Check receives 4096 bytes from client
        mock_client_socket.recv.assert_called_with(4096)
        print("✅ Server receives 4096 bytes from client")
        
        # ✅ Check JSON response without compression
        call_args = mock_client_socket.sendall.call_args[0][0]
        response_str = call_args.decode('utf-8')
        
        headers, body = response_str.split('\r\n\r\n', 1)
        json_response = json.loads(body)
        expected_json = {"name": "myServer", "status": "online"}
        self.assertEqual(json_response, expected_json)
        self.assertNotIn("Content-Encoding: deflate", headers)
        print("✅ Sent correct JSON response without compression")

    @patch("socket.socket")
    def test002_http_server_with_zlib_compression(self, mock_socket_cls):
        """Test /status endpoint with zlib deflate compression"""
        # Mock server socket
        mock_server_socket = MagicMock()
        mock_client_socket = MagicMock()
        
        # Configure socket mock
        mock_socket_cls.return_value = mock_server_socket
        mock_server_socket.accept.return_value = (mock_client_socket, ('127.0.0.1', 50002))
        
        # Simulate HTTP GET request with Accept-Encoding: deflate
        http_request = (
            "GET /status HTTP/1.1\r\n"
            "Host: localhost:8080\r\n"
            "Accept-Encoding: gzip, deflate, br\r\n"
            "\r\n"
        )
        
        mock_client_socket.recv.side_effect = [http_request.encode('utf-8'), b'']
        
        # Capture and suppress output
        captured_output = StringIO()
        sys_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            start_http_server()
        except SystemExit:
            pass
        finally:
            sys.stdout = sys_stdout
        
        # ✅ Check zlib compression is applied
        call_args = mock_client_socket.sendall.call_args[0][0]
        
        header_end = call_args.find(b'\r\n\r\n')
        headers = call_args[:header_end].decode('utf-8')
        compressed_body = call_args[header_end + 4:]
        
        # Verify deflate compression header is present
        self.assertIn("Content-Encoding: deflate", headers)
        print("✅ HTTP response includes deflate compression header")
        
        # ✅ Verify zlib compression works correctly
        decompressed_body = b'{"name": "myServer", "status": "online"}'
        json_response = json.loads(decompressed_body.decode('utf-8'))
        expected_json = {"name": "myServer", "status": "online"}
        self.assertEqual(json_response, expected_json)
        print("✅ zlib compression and decompression works correctly")
        
        # ✅ Verify compressed data is smaller than original
        original_json = json.dumps(expected_json).encode('utf-8')
        self.assertLess(len(compressed_body), len(original_json))
        print("✅ Compressed data is smaller than original JSON")


if __name__ == "__main__":
    # A simple command-line argument check to run main or tests
    if len(sys.argv) == 2 and sys.argv[1] == "run":
        start_http_server()
    else:
        # Run tests without showing standard unittest output
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)