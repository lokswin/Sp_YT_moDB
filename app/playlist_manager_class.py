# file: app/playlist_manager_class.py
import json
import os
import re
import requests
import pymongo
import logging
from spotipy import Spotify
from app.oauth_service_child_classes import YouTubeMusicOAuth, SpotifyOAuth, MongoOAuth
from app.callback_server import CallbackHandler

class PlaylistManager:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.spotify_session = None
        self.db = None
        self.load_env()
        self.tokens = {
            'spotify': None,
            'youtube_music': None,
            'mongo': None
        }

    def load_env(self):
        self.spotify_client_id = self.config['spotify_client_id']
        self.spotify_client_secret = self.config['spotify_client_secret']
        self.playlist_links_file = self.config['playlist_links_file']
        self.json_temp_folder = self.config['json_temp_folder']
        self.mongo_client_id = self.config['mongo_client_id']
        self.mongo_client_secret = self.config['mongo_client_secret']
        self.spotify_auth_url = self.config['spotify_auth_url']
        self.spotify_token_url = self.config['spotify_token_url']
        self.spotify_redirect_url = self.config['spotify_redirect_url']
        self.youtube_client_id = self.config['youtube_client_id']
        self.youtube_client_secret = self.config['youtube_client_secret']
        self.youtube_auth_url = self.config['youtube_auth_url']
        self.youtube_token_url = self.config['youtube_token_url']
        self.mongo_auth_url = self.config['mongo_auth_url']
        self.mongo_token_url = self.config['mongo_token_url']

    def authenticate(self, service_name):
        self.logger.info(f"Authenticating {service_name.capitalize()}...")
        if service_name == 'spotify':
            oauth_service = SpotifyOAuth(
                client_id=self.spotify_client_id,
                client_secret=self.spotify_client_secret,
                authorization_base_url=self.spotify_auth_url,
                token_url=self.spotify_token_url,
                service_name='spotify',
                redirect_uri=self.spotify_redirect_url
            )
        elif service_name == 'youtube_music':
            oauth_service = YouTubeMusicOAuth(
                client_id=self.youtube_client_id,
                client_secret=self.youtube_client_secret,
                authorization_base_url=self.youtube_auth_url,
                token_url=self.youtube_token_url,
                service_name='youtube_music',
                redirect_uri=self.spotify_redirect_url
            )
        elif service_name == 'mongo':
            oauth_service = MongoOAuth(
                client_id=self.mongo_client_id,
                client_secret=self.mongo_client_secret,
                authorization_base_url=self.mongo_auth_url,
                token_url=self.mongo_token_url,
                service_name='mongo',
                redirect_uri=self.spotify_redirect_url  # Assuming the same redirect URL for Mongo
            )
        else:
            self.logger.error(f"Unknown service: {service_name}")
            return
        
        self._authenticate_with_server(oauth_service, service_name)

    def _authenticate_with_server(self, oauth_service, service_name):
        oauth_service.authenticate()
        authorization_code = CallbackHandler.authorization_code
        if authorization_code:
            tokens = oauth_service.get_token(authorization_code)
            oauth_service.save_tokens(tokens)
            self.tokens[service_name] = tokens
            self.logger.info(f"{service_name.capitalize()} authentication successful.")
        else:
            self.logger.error(f"Failed to retrieve authorization code for {service_name}.")

    def read_playlist_links(self):
        with open(self.playlist_links_file, 'r') as file:
            return [line.strip() for line in file]

    def generate_json_from_playlist(self, playlist_link):
        self.logger.info(f"Generating JSON from playlist: {playlist_link}")
        spotify_oauth = SpotifyOAuth(
            client_id=self.spotify_client_id,
            client_secret=self.spotify_client_secret,
            authorization_base_url=self.spotify_auth_url,
            token_url=self.spotify_token_url,
            service_name='spotify',
            redirect_uri=self.spotify_redirect_url
        )
        spotify_oauth.authenticate()
        access_token = spotify_oauth.load_tokens().get('access_token')
        self.spotify_session = Spotify(auth=access_token)

        playlist_id = re.findall(r'playlist/(\w+)', playlist_link)[0]
        playlist = self.spotify_session.playlist(playlist_id)
        playlist_name = playlist["name"]
        tracks = [{
            "name": item["track"]["name"],
            "artist": item["track"]["artists"][0]["name"]
        } for item in playlist["tracks"]["items"]]

        playlist_data = {
            "playlist_name": playlist_name,
            "tracks": tracks
        }

        if not os.path.exists(self.json_temp_folder):
            os.makedirs(self.json_temp_folder)
        json_file_path = os.path.join(self.json_temp_folder, f"{playlist_data['playlist_name']}.json")
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(playlist_data, json_file, ensure_ascii=False, indent=4)
        self.logger.info(f"JSON generated for playlist: {playlist_name}")

    def upload_to_youtube_music(self):
        self.logger.info("Uploading to YouTube Music...")
        youtube_music_oauth = YouTubeMusicOAuth(
            client_id=self.youtube_client_id,
            client_secret=self.youtube_client_secret,
            authorization_base_url=self.youtube_auth_url,
            token_url=self.youtube_token_url,
            service_name='youtube_music',
            redirect_uri=self.spotify_redirect_url
        )
        self._authenticate_with_server(youtube_music_oauth, 'youtube_music')
        access_token = youtube_music_oauth.load_tokens().get('access_token')

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

        for json_file in os.listdir(self.json_temp_folder):
            if json_file.endswith('.json'):
                with open(os.path.join(self.json_temp_folder, json_file), 'r', encoding='utf-8') as file:
                    playlist_data = json.load(file)
                playlist_name = playlist_data["playlist_name"]

                create_playlist_response = requests.post(
                    "https://www.googleapis.com/youtube/v3/playlists",
                    headers=headers,
                    json={
                        "snippet": {
                            "title": playlist_name,
                            "description": "Created by Playlist Manager",
                            "tags": ["Playlist Manager", "YouTube Music"],
                            "defaultLanguage": "en"
                        },
                        "status": {
                            "privacyStatus": "private"
                        }
                    }
                )
                playlist_id = create_playlist_response.json()["id"]

                for track in playlist_data["tracks"]:
                    search_response = requests.get(
                        "https://www.googleapis.com/youtube/v3/search",
                        headers=headers,
                        params={
                            "part": "snippet",
                            "q": f"{track['name']} {track['artist']}",
                            "type": "video",
                            "maxResults": 1
                        }
                    )
                    video_id = search_response.json()["items"][0]["id"]["videoId"]

                    requests.post(
                        f"https://www.googleapis.com/youtube/v3/playlistItems",
                        headers=headers,
                        json={
                            "snippet": {
                                "playlistId": playlist_id,
                                "resourceId": {
                                    "kind": "youtube#video",
                                    "videoId": video_id
                                }
                            }
                        }
                    )
        self.logger.info("Upload to YouTube Music completed.")

    def is_authorized(self, service_name):
        return self.tokens.get(service_name) is not None

    def logout(self, service_name):
        self.logger.info(f"Logging out from {service_name.capitalize()}...")
        self.tokens[service_name] = None
        self.save_tokens()
        self.logger.info(f"Logged out from {service_name.capitalize()}.")

    def save_tokens(self):
        with open('tokens.json', 'w') as file:
            json.dump(self.tokens, file)

    def load_tokens(self):
        if os.path.exists('tokens.json'):
            with open('tokens.json', 'r') as file:
                self.tokens = json.load(file)
