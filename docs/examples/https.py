from http.server import HTTPServer, SimpleHTTPRequestHandler
from poorconn import close_upon_acceptance, make_socket_patchable
from ssl import PROTOCOL_TLS_SERVER, SSLContext

with HTTPServer(("localhost", 8888), SimpleHTTPRequestHandler) as httpd:
    context = SSLContext(PROTOCOL_TLS_SERVER)
    # Replace with your cert and key files
    context.load_cert_chain(certfile="/path/to/server.pem", keyfile="/path/to/server.key")
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    httpd.socket = make_socket_patchable(httpd.socket)
    close_upon_acceptance(httpd.socket)
    print(f"Start serving at https://{httpd.server_address[0]}:{httpd.server_address[1]}")
    httpd.serve_forever()
