# file: app\oauth_service_base_class.py
import requests, time, webbrowser, threading
from urllib.parse import urlencode
from app.callback_server import CallbackHandler, run_server

class OAuthService:
    def __init__(self, client_id, client_secret, authorization_base_url, token_url, service_name, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization_base_url = authorization_base_url
        self.token_url = token_url
        self.service_name = service_name
        self.redirect_uri = redirect_uri
        self.tokens = {}

    def get_authorization_url(self):
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': self.get_scope()
        }
        url = f"{self.authorization_base_url}?{urlencode(params)}"
        return url

    def authenticate(self):
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()

        auth_url = self.get_authorization_url()
        webbrowser.open(auth_url)
        print("Please authorize the application in your browser.")
        
        self.wait_for_authorization_code()

    def wait_for_authorization_code(self):
        while CallbackHandler.authorization_code is None:
            time.sleep(1)  # Wait until the authorization code is received

        authorization_code = CallbackHandler.authorization_code
        tokens = self.get_token(authorization_code)
        self.save_tokens(tokens)

    def get_scope(self):
        raise NotImplementedError("Subclasses should implement this!")

    def get_token(self, authorization_code):
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        response = requests.post(self.token_url, data=data)
        return response.json()

    def save_tokens(self, tokens):
        self.tokens = tokens

    def load_tokens(self):
        return self.tokens
