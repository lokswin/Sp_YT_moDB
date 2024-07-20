from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse
import threading

class CallbackHandler(BaseHTTPRequestHandler):
    authorization_code = None

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        query_params = urlparse.parse_qs(parsed_path.query)
        CallbackHandler.authorization_code = query_params.get('code', [None])[0]
        if CallbackHandler.authorization_code:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorization successful! You can close this window.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error: No authorization code provided.")

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CallbackHandler)
    httpd.timeout = 60  # Timeout to stop the server automatically after 1 minute
    threading.Thread(target=httpd.serve_forever).start()
