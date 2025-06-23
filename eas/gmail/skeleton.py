import smtplib
import unittest
import sys
from unittest.mock import patch, MagicMock
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from io import StringIO


def send_gmail():
    # Static inputs (replace with your own test values if needed)
    GMAIL_USER = "sender@gmail.com"
    GMAIL_PASSWORD = "gmailpassword"
    recipient_email = "receiver@gmail.com"
    recipient_name = "Alice"

    # define the subject and message
    subject = "subject"
    message= f"Hello, this is a test email."

    # define the SMTP server and port
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # create an SMTP connection
    server = smtplib.SMTP(smtp_server, smtp_port)

    # start TLS for security
    server.starttls()

    # login to the server
    server.login(GMAIL_USER, GMAIL_PASSWORD)

    # create the email message
    msg = MIMEMultipart()
    msg['From'] = recipient_name
    msg['To'] = recipient_email
    msg['Subject'] = subject

    body = f"Dear {recipient_name}, {message}"

    # send the email
    server.sendmail(GMAIL_USER, recipient_email, body)  

    # print a confirmation message
    print(f"Email sent to {recipient_email}")
    
    # close the server connection
    server.quit()


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')


class TestGmailSender(unittest.TestCase):
    @patch('smtplib.SMTP')
    def test_send_gmail(self, mock_smtp):
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        # Execute the function
        send_gmail()

        # SMTP connection checks
        mock_smtp.assert_called_with("smtp.gmail.com", 587)
        print(f"mock_smtp.call_args: {mock_smtp.call_args}")

        # Check starting TLS
        mock_server.starttls.assert_called_once()

        # verify login to the server
        mock_server.login.assert_called_with("sender@gmail.com", "gmailpassword")
        print(f"mock_server.login.call_args: {mock_server.login.call_args}")

        # verify quitting the server
        mock_server.quit.assert_called_once()
        
        # verify sending the email
        mock_server.sendmail.assert_called_once()
        print(f"mock_server.sendmail.call_args: {mock_server.sendmail.call_args}")

        # Email content verification
        sendmail_args = mock_server.sendmail.call_args[0]
        fromaddr = sendmail_args[0]
        toaddr = sendmail_args[1]
        email_body = sendmail_args[2]
        receiver_name = "Alice"
        message = "Hello, this is a test email."

        # assert the email was sent with the correct parameters
        assert_equal(fromaddr, "sender@gmail.com")
        assert_equal(toaddr, "receiver@gmail.com")
        assert_equal(email_body, f"Dear {receiver_name}, {message}")

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        # If the script is run with 'run' argument, execute the program
        send_gmail()

    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
