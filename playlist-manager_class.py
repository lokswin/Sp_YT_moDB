import os
import json
import re
from datetime import datetime, timedelta
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import pymongo

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
        self.mongo_username = self.config['mongo_username']
        self.mongo_password = self.config['mongo_password']

    def authenticate_spotify(self):
        client_credentials_manager = SpotifyClientCredentials(
            client_id=self.spotify_client_id, client_secret=self.spotify_client_secret
        )
        self.spotify_session = Spotify(client_credentials_manager=client_credentials_manager)

    def read_playlist_links(self):
        with open(self.playlist_links_file, 'r') as file:
            return [line.strip() for line in file]

    def generate_json_from_playlist(self, playlist_link):
        playlist_id = re.match(r"https://open.spotify.com/playlist/(.*)\?", playlist_link).groups()[0]
        tracks = self.spotify_session.playlist_tracks(playlist_id)["items"]
        playlist_name = self.spotify_session.playlist(playlist_id)["name"]

        playlist_data = {
            "playlist_name": playlist_name,
            "tracks": [
                {"name": track["track"]["name"], "artist": ", ".join([artist["name"] for artist in track["track"]["artists"]])}
                for track in tracks
            ]
        }

        os.makedirs(self.json_temp_folder, exist_ok=True)
        json_file_path = os.path.join(self.json_temp_folder, f"{playlist_name}.json")
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(playlist_data, json_file, ensure_ascii=False, indent=4)

    def upload_jsons_to_mongodb(self):
        client = pymongo.MongoClient(f"mongodb+srv://{self.mongo_username}:{self.mongo_password}@cluster0.mongodb.net/test?retryWrites=true&w=majority")
        db = client.test
        collection = db.playlists
        for json_file in os.listdir(self.json_temp_folder):
            if json_file.endswith('.json'):
                with open(os.path.join(self.json_temp_folder, json_file), 'r', encoding='utf-8') as file:
                    playlist_data = json.load(file)
                collection.update_one({"playlist_name": playlist_data["playlist_name"]}, {"$set": playlist_data}, upsert=True)

    def download_jsons_from_mongodb(self):
        client = pymongo.MongoClient(f"mongodb+srv://{self.mongo_username}:{self.mongo_password}@cluster0.mongodb.net/test?retryWrites=true&w=majority")
        db = client.test
        collection = db.playlists
        os.makedirs(self.json_temp_folder, exist_ok=True)
        for playlist_data in collection.find():
            json_file_path = os.path.join(self.json_temp_folder, f"{playlist_data['playlist_name']}.json")
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(playlist_data, json_file, ensure_ascii=False, indent=4)

    def upload_to_youtube_music(self):
        youtube_music_oauth = YouTubeMusicOAuth(self.config['youtube_client_id'], self.config['youtube_client_secret'])
        youtube_music_oauth.set_mongo_credentials(self.mongo_username, self.mongo_password)
        access_token = youtube_music_oauth.get_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

        for json_file in os.listdir(self.json_temp_folder):
            if json_file.endswith('.json'):
                with open(os.path.join(self.json_temp_folder, json_file), 'r', encoding='utf-8') as file:
                    playlist_data = json.load(file)
                playlist_name = playlist_data["playlist_name"]

                # Create YouTube Music playlist (this is a placeholder, replace with actual YouTube Music API call)
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

                # Add tracks to YouTube Music playlist (this is a placeholder, replace with actual YouTube Music API call)
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
