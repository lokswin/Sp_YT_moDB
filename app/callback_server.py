# file: app\callback_server.py
import http.server
import socketserver
import threading
from urllib.parse import urlparse, parse_qs

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    authorization_code = None

    def do_GET(self):
        if self.path.startswith("/callback"):
            query = urlparse(self.path).query
            params = parse_qs(query)
            code = params.get('code', [None])[0]
            if code:
                CallbackHandler.authorization_code = code
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"Authorization code received. You may close this window.")
                threading.Thread(target=self.server.shutdown).start()  # Stop the server after handling the request
            else:
                self.send_error(400, "Authorization code not found")
        else:
            self.send_error(404, "Not found")

def run_server(port=8000):
    with socketserver.TCPServer(("", port), CallbackHandler) as httpd:
        print(f"Serving at port {port}")
        httpd.serve_forever()
