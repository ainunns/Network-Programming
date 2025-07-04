import json
import socket
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from datetime import datetime
import sys

class Message:
    def __init__(self, username, text, timestamp=None):
        self.username = username
        self.text = text
        self.timestamp = timestamp

    def serialize(self):
        # Create a dictionary with the message data and serialize it into a JSON string using the json module.
        message_dict = {
            "username": self.username,
            "text": self.text,
            "timestamp": self.timestamp
        }

        return json.dumps(message_dict)

    @staticmethod
    def deserialize(serialized_message):
        # Parse the JSON string back into a Python dictionary.
        data = json.loads(serialized_message)

        # Create a new Message object using the data from the dictionary.
        message = Message(data["username"], data["text"], data["timestamp"])

        return message

def main():
    username = input("Enter your username: ")
    text = input("Enter your message: ")

    message = Message(username, text)
    serialized_message = message.serialize()

    # Create a TCP socket.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            # Connect to the server
            sock.connect(("localhost", 12345))

            # Send the serialized message to the server.
            sock.sendall(serialized_message.encode("utf-8"))
        except ConnectionRefusedError:
            print("Connection failed. Is the server running?")


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f"test attribute passed: {parameter1} is equal to {parameter2}")
    else:
        print(f"test attribute failed: {parameter1} is not equal to {parameter2}")


class TestChatClient(unittest.TestCase):

    def test_message_serialization(self):
        username = "Gracie"
        text = "Hello, World!"
        message = Message(username, text)
        serialized_message = message.serialize()

        # Deserialize to verify
        deserialized_message = Message.deserialize(serialized_message)

        assert_equal(deserialized_message.username, username)
        assert_equal(deserialized_message.text, text)
        # Verify timestamp is a valid datetime string
        self.assertIsInstance(
            datetime.strptime(deserialized_message.timestamp, "%Y-%m-%d %H:%M:%S.%f"),
            datetime,
        )

    @patch("builtins.input", side_effect=["Gracie", "Hello, World!"])
    @patch("socket.socket")
    def test_client_main(self, mock_socket_class, mock_input):
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket_instance

        main()

        # Check if the connect method was called with the correct parameters
        mock_socket_instance.connect.assert_called_once_with(("localhost", 12345))
        # Check if the sendall method was called
        self.assertTrue(mock_socket_instance.sendall.called, "sendall was not called")

        # Get the arguments with which sendall was called
        sent_data_bytes = mock_socket_instance.sendall.call_args[0][0]
        # Decode bytes to string to deserialize from JSON
        sent_data_str = sent_data_bytes.decode("utf-8")
        deserialized_message = Message.deserialize(sent_data_str)

        assert_equal(deserialized_message.text, "Hello, World!")
        assert_equal(deserialized_message.username, "Gracie")
        self.assertIsInstance(
            datetime.strptime(deserialized_message.timestamp, "%Y-%m-%d %H:%M:%S.%f"),
            datetime,
        )


if __name__ == "__main__":
    # A simple command-line argument check to run main or tests
    if len(sys.argv) == 2 and sys.argv[1] == "run":
        main()
    else:
        # Run tests without showing standard unittest output
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
