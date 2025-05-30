import socket
import ssl

HOST = 'www.google.com'
PORT = 443

def get_ssl_certificate(hostname, port):
  # Establish SSL connection and retrieve peer certificate
  context = ssl.create_default_context()
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
      ssock.connect((hostname, port))
      cert = ssock.getpeercert()
  return cert

if __name__ == '__main__':
  try:
    certificate = get_ssl_certificate(HOST, PORT)
    
    # Get Common Name from subject
    subject = dict(x[0] for x in certificate['subject'])
    cn = subject.get('commonName', 'N/A')
    print(f"Common Name (CN): {cn}")
    
    # Check required fields
    required_fields = ['subject', 'issuer']
    has_fields = all(field in certificate for field in required_fields)
    if has_fields:
        print(f"Certificate has all required fields: {required_fields}")
    else:
        missing_fields = [field for field in required_fields if field not in certificate]
        print(f"Certificate is missing required fields: {missing_fields}")
      
  except Exception as e:
    print(f"An error occurred while retrieving the SSL certificate: {e}")