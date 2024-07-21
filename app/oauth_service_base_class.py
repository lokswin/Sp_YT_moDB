import webbrowser
import requests
from urllib.parse import urlencode
import json
import logging

class OAuthService:
    def __init__(self, client_id, client_secret, authorization_base_url, token_url, service_name, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization_base_url = authorization_base_url
        self.token_url = token_url
        self.service_name = service_name
        self.redirect_uri = redirect_uri

    def get_authorization_url(self):
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.get_scope(),
            'access_type': 'offline'
        }
        url = f"{self.authorization_base_url}?{urlencode(params)}"
        return url

    def get_scope(self):
        return ''

    def get_token(self, authorization_code):
        data = {
            'code': authorization_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        response = requests.post(self.token_url, data=data)
        if response.status_code != 200:
            logging.error(f"Failed to get token: {response.text}")
            raise Exception(f"Failed to get token: {response.text}")
        return response.json()

    def authenticate(self):
        auth_url = self.get_authorization_url()
        webbrowser.open(auth_url)
        print("Please authorize the application in your browser and paste the authorization code here.")
        authorization_code = input("Enter the authorization code: ")
        tokens = self.get_token(authorization_code)
        self.save_tokens(tokens)

    def save_tokens(self, tokens):
        with open(f"{self.service_name}_tokens.json", 'w') as f:
            json.dump(tokens, f)
        logging.info(f"Tokens saved for {self.service_name}")

    def load_tokens(self):
        try:
            with open(f"{self.service_name}_tokens.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Token file not found for {self.service_name}")
            return None

    def refresh_tokens(self):
        tokens = self.load_tokens()
        if tokens:
            refresh_token = tokens.get('refresh_token')
            if refresh_token:
                data = {
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token
                }
                response = requests.post(self.token_url, data=data)
                if response.status_code != 200:
                    logging.error(f"Failed to refresh token: {response.text}")
                    raise Exception(f"Failed to refresh token: {response.text}")
                new_tokens = response.json()
                self.save_tokens(new_tokens)
                return new_tokens
        return None
