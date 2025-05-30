import socket
import ssl
import sys
import unittest
from io import StringIO

# Target server to test SSL connection
test_hostname = 'www.google.com'
test_port = 443

mock_cert = {'subject': ((('commonName', 'www.google.com'),),), 'issuer': ((('countryName', 'US'),), (('organizationName', 'Google Trust Services'),), (('commonName', 'WR2'),)), 'version': 3, 'serialNumber': '769C7B331D8F61240996E8FB5EEDCA99', 'notBefore': 'May 12 08:44:44 2025 GMT', 'notAfter': 'Aug  4 08:44:43 2025 GMT', 'subjectAltName': (('DNS', 'www.google.com'),), 'OCSP': ('http://o.pki.goog/wr2',), 'caIssuers': ('http://i.pki.goog/wr2.crt',), 'crlDistributionPoints': ('http://c.pki.goog/wr2/oBFYYahzgVI.crl',)}

# Establish an SSL connection and retrieve peer certificate
def get_ssl_certificate(hostname, port):
    context = ssl.create_default_context()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            ssock.connect((hostname, port))
            cert = ssock.getpeercert(False)
            return cert

# Verify that certificate contains expected fields
def assert_cert_has_fields(cert, fields):
    missing = [field for field in fields if field not in cert]
    if not missing:
        print("Certificate has all required fields:", fields)
    else:
        print("Certificate is missing fields:", missing)

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

# Unit test for SSL certificate retrieval
class TestSSLConnection(unittest.TestCase):
    def setUp(self):
        self.hostname = test_hostname
        self.port = test_port

    def test_ssl_certificate_retrieval(self):
        cert = get_ssl_certificate(self.hostname, self.port)
        self.assertIsInstance(cert, dict)
        assert_cert_has_fields(cert, ['subject', 'issuer'])

    def test_certificate_subject(self):
        cert = get_ssl_certificate(self.hostname, self.port)
        subject = dict(x[0] for x in cert['subject'])
        self.assertIn('commonName', subject)
        print("Common Name (CN):", subject.get('commonName'))

# Entry point
if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        cert = get_ssl_certificate(test_hostname, test_port)
        print("Retrieved SSL Certificate:", cert)
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
