import xml.etree.ElementTree as ET
from datetime import datetime
import socket
import sys
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO


class Message:
    def __init__(self, username, text):
        self.username = username
        self.text = text
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    def serialize(self):
        # you can use xml.etree.ElementTree module
        root = ET.Element('message')
        username_element = ET.SubElement(root, 'username')
        username_element.text = self.username
        text_element = ET.SubElement(root, 'text')
        text_element.text = self.text
        timestamp_element = ET.SubElement(root, 'timestamp')
        timestamp_element.text = self.timestamp
        
        return ET.tostring(root, encoding='utf-8').decode('utf-8')

    @staticmethod
    def deserialize(serialized_message):
        # extract the username, text, and timestamp from the XML-serialized message
        message_element = ET.fromstring(serialized_message)
        username = message_element.find('username').text
        text = message_element.find('text').text
        timestamp = message_element.find('timestamp').text

        # create a new Message object with the extracted data
        message = Message(username, text)

        return message

def main():
    username = input("Enter your username: ")
    text = input("Enter your message: ")

    message = Message(username, text)
    serialized_message = message.serialize()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # connect to the server 
        s.connect(('localhost', 12345))

        # send the serialized message to the server
        s.sendall(serialized_message.encode('utf-8'))

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')

class TestChatClient(unittest.TestCase):

    def test_message_serialization(self):
        username = "Alice"
        text = "Hello, World!"
        message = Message(username, text)
        serialized_message = message.serialize()
        
        # Deserialize to verify
        deserialized_message = Message.deserialize(serialized_message)
        
        assert_equal(deserialized_message.username, username)
        assert_equal(deserialized_message.text, text)
        self.assertIsInstance(datetime.strptime(deserialized_message.timestamp, '%Y-%m-%d %H:%M:%S.%f'), datetime)

    @patch('builtins.input', side_effect=['Alice', 'Hello, World!'])
    @patch('socket.socket')
    def test_client_main(self, mock_socket_class, mock_input):
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket_instance
        
        main()
        
        # Check if the connect method was called with the correct parameters
        mock_socket_instance.connect.assert_called_once_with(('localhost', 12345))
        # Check if the sendall method was called at least once
        self.assertTrue(mock_socket_instance.sendall.called, "sendall was not called")
        
        # Get the arguments with which sendall was called
        sent_data = mock_socket_instance.sendall.call_args[0][0]
        deserialized_message = Message.deserialize(sent_data)
        
        assert_equal(deserialized_message.text, 'Hello, World!')
        assert_equal(deserialized_message.username, 'Alice')
        self.assertIsInstance(datetime.strptime(deserialized_message.timestamp, '%Y-%m-%d %H:%M:%S.%f'), datetime)

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        main()
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
