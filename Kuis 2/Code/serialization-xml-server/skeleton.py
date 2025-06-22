import xml.etree.ElementTree as ET
import socket

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Message:
    def __init__(self, username, text, timestamp):
        self.username = username
        self.text = text
        self.timestamp = timestamp

    @staticmethod
    def deserialize(serialized_message):
        # extract the username, text, and timestamp from the XML-serialized message
        
        return ?

    def serialize(self):
        # serialize the message object to an XML string
        ?
        return ?

def main():
    # create a server socket, bind, listen
    server_socket = ?
    ?
    ?
    server_socket.setblocking(False)

    # list of sockets for select.select()
    sockets_list = ?

    logger.info(?)

    while True:
        # select.select() 
        read_sockets, _, exception_sockets = ?

        for notified_socket in ?:
            if notified_socket == ?:
                # accept new connection
                client_socket, client_address = ?
                client_socket.setblocking(False)

                # add the new client socket to the list of sockets
                ?
                logger.info(f"Accepted new connection from {?}")
            else:
                try:
                    # receive message from client
                    data = ?
                    if data:
                        message = ?
                        logger.info("Received message:")
                        logger.info(f"Username: {?}")
                        logger.info(f"Text: {?}")
                        logger.info(f"Timestamp: {?}")
                except Exception as e:
                    logger.info(f"Exception: {e}")
                    # remove the socket that's broken
                    ?
                    # close the connection
                    ?)

        for notified_socket in exception_sockets:
            # remove the socket
            ?
            # close the connection
            ?

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

def assert_true_any(parameter1, parameter2):
    found = False
    for message in parameter2:
        if parameter1 in message:
            found = True
            break
    
    print(f'test attribute passed: {parameter1} found in log messages' if found else f'test attribute failed: {parameter1} not found in log messages')
    # return found

class TestChatServer(unittest.TestCase):
    
    @patch('select.select')
    @patch('socket.socket')
    def test_server_main(self, mock_socket_class, mock_select):
        mock_server_socket = MagicMock()
        mock_client_socket = MagicMock()
        
        mock_socket_class.return_value = mock_server_socket
        mock_server_socket.accept.return_value = (mock_client_socket, ('127.0.0.1', 54321))
        
        # Initial call to select() returns the server socket as ready to accept
        mock_select.side_effect = [
            ([mock_server_socket], [], []),
            ([mock_client_socket], [], []),
            KeyboardInterrupt()  # To break out of the infinite loop
        ]
        
        # Mock data received from the client
        test_message = Message("Alice", "Hello, World!", datetime.now())
        serialized_message = test_message.serialize()
        mock_client_socket.recv.return_value = serialized_message
        
        with self.assertLogs(logger, level='INFO') as log:
            with self.assertRaises(KeyboardInterrupt):
                main()
            
            # Check if the server accepted a new connection
            mock_server_socket.accept.assert_called_once()
            mock_client_socket.setblocking.assert_called_once_with(False)
            
            # Check if the server received and deserialized the message correctly
            mock_client_socket.recv.assert_called_once_with(1024)
            
            # Verify log messages
            log_output = log.output
            
            assert_true_any("Received message:", log_output)
            assert_true_any("Username: Alice", log_output)
            assert_true_any("Text: Hello, World!", log_output) 

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        main()
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
