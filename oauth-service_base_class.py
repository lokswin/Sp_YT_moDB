import requests
from requests_oauthlib import OAuth2Session
import pymongo
import json
from datetime import datetime, timedelta

class OAuthService:
    def __init__(self, client_id, client_secret, authorization_base_url, token_url, service_name):
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization_base_url = authorization_base_url
        self.token_url = token_url
        self.service_name = service_name
        self.oauth_session = OAuth2Session(client_id)

    def initiate_authorization(self):
        authorization_url, _ = self.oauth_session.authorization_url(self.authorization_base_url)
        print(f"Please go to the following URL and authorize the app:\n{authorization_url}")
        return self.oauth_session

    def fetch_token(self, authorization_response):
        self.oauth_session.fetch_token(self.token_url, authorization_response=authorization_response, client_secret=self.client_secret)
        return self.oauth_session.token

    def get_token(self):
        tokens = self._retrieve_tokens_from_mongo()
        if tokens:
            if self._is_token_expired(tokens):
                tokens = self._refresh_token(tokens)
            return tokens['access_token']
        return None

    def _retrieve_tokens_from_mongo(self):
        client = pymongo.MongoClient(f"mongodb+srv://{self.mongo_username}:{self.mongo_password}@cluster0.mongodb.net/test?retryWrites=true&w=majority")
        db = client.test
        tokens_collection = db.auth_tokens
        tokens = tokens_collection.find_one({"_id": self.service_name})
        return tokens

    def _is_token_expired(self, tokens):
        return tokens['expires_at'] <= datetime.utcnow()

    def _refresh_token(self, tokens):
        response = requests.post(
            self.token_url,
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': tokens['refresh_token'],
                'grant_type': 'refresh_token'
            }
        )
        new_tokens = response.json()
        new_tokens['_id'] = self.service_name
        new_tokens['expires_at'] = datetime.utcnow() + timedelta(seconds=new_tokens['expires_in'])
        self._store_tokens_to_mongo(new_tokens)
        return new_tokens

    def _store_tokens_to_mongo(self, tokens):
        client = pymongo.MongoClient(f"mongodb+srv://{self.mongo_username}:{self.mongo_password}@cluster0.mongodb.net/test?retryWrites=true&w=majority")
        db = client.test
        tokens_collection = db.auth_tokens
        tokens_collection.update_one({"_id": self.service_name}, {"$set": tokens}, upsert=True)

    def set_mongo_credentials(self, username, password):
        self.mongo_username = username
        self.mongo_password = password
