import os
import json
import re
import requests
import logging
import pymongo
from spotipy import Spotify
from app.callback_server import run_server
from app.oauth_service_child_classes import YouTubeMusicOAuth, SpotifyOAuth, MongoOAuth
from spotipy.oauth2 import SpotifyClientCredentials

class PlaylistManager:
    def __init__(self, config):
        self.config = config
        self.spotify_session = None
        self.db = None
        self.load_env()

    def load_env(self):
        self.spotify_client_id = self.config['spotify_client_id']
        self.spotify_client_secret = self.config['spotify_client_secret']
        self.playlist_links_file = self.config['playlist_links_file']
        self.json_temp_folder = self.config['json_temp_folder']
        self.mongo_client_id = self.config['mongo_client_id']
        self.mongo_client_secret = self.config['mongo_client_secret']
        self.spotify_auth_url = self.config['spotify_auth_url']
        self.spotify_token_url = self.config['spotify_token_url']
        self.youtube_client_id = self.config['youtube_client_id']
        self.youtube_client_secret = self.config['youtube_client_secret']
        self.youtube_auth_url = self.config['youtube_auth_url']
        self.youtube_token_url = self.config['youtube_token_url']
        self.mongo_auth_url = self.config['mongo_auth_url']
        self.mongo_token_url = self.config['mongo_token_url']

    def authenticate_spotify(self):
        spotify_oauth = SpotifyOAuth(
            self.spotify_client_id, 
            self.spotify_client_secret, 
            self.spotify_auth_url, 
            self.spotify_token_url, 
            'Spotify', 
            'http://localhost:8000/callback'
        )
        self._authenticate_with_server(spotify_oauth)

    def authenticate_mongo(self):
        mongo_oauth = MongoOAuth(
            self.mongo_client_id, 
            self.mongo_client_secret, 
            self.mongo_auth_url, 
            self.mongo_token_url, 
            'MongoDB', 
            'http://localhost:8000/callback'
        )
        self._authenticate_with_server(mongo_oauth)
        access_token = mongo_oauth.load_tokens().get('access_token')
        self.db = pymongo.MongoClient(
            f"mongodb+srv://{access_token}@cluster0.mongodb.net/test?retryWrites=true&w=majority"
        ).test

    def _authenticate_with_server(self, oauth_service):
        run_server()
        oauth_service.authenticate()
        authorization_code = CallbackHandler.authorization_code
        if authorization_code:
            tokens = oauth_service.get_token(authorization_code)
            oauth_service.save_tokens(tokens)
        else:
            logging.error("Failed to retrieve authorization code.")

    def read_playlist_links(self):
        with open(self.playlist_links_file, 'r') as file:
            return [line.strip() for line in file]

    def generate_json_from_playlist(self, playlist_link):
        spotify_oauth = SpotifyOAuth(
            self.spotify_client_id, 
            self.spotify_client_secret, 
            self.spotify_auth_url, 
            self.spotify_token_url, 
            'Spotify', 
            'http://localhost:8000/callback'
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

    def upload_to_youtube_music(self):
        youtube_music_oauth = YouTubeMusicOAuth(
            self.youtube_client_id, 
            self.youtube_client_secret, 
            self.youtube_auth_url, 
            self.youtube_token_url, 
            'YouTubeMusic', 
            'http://localhost:8000/callback'
        )
        self._authenticate_with_server(youtube_music_oauth)
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
