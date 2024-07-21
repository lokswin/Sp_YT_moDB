import tkinter as tk
from tkinter import messagebox

class GUI:
    def __init__(self, playlist_manager, logger):
        self.playlist_manager = playlist_manager
        self.logger = logger

        self.root = tk.Tk()
        self.root.title("Playlist Manager")

        self.create_widgets()
        self.root.mainloop()

    def create_widgets(self):
        tk.Button(self.root, text="Login to Spotify", command=self.login_to_spotify).pack()
        tk.Button(self.root, text="Generate JSONs", command=self.generate_jsons).pack()
        tk.Button(self.root, text="Upload to MongoDB", command=self.upload_to_mongodb).pack()
        tk.Button(self.root, text="Download from MongoDB", command=self.download_from_mongodb).pack()
        tk.Button(self.root, text="Upload to YouTube Music", command=self.upload_to_youtube_music).pack()
        tk.Button(self.root, text="Toggle Debug", command=self.toggle_debug).pack()

    def login_to_spotify(self):
        self.playlist_manager.authenticate_spotify()
        self.logger.info("Logged in to Spotify.")

    def generate_jsons(self):
        playlist_links = self.playlist_manager.read_playlist_links()
        for link in playlist_links:
            self.playlist_manager.generate_json_from_playlist(link)
        self.logger.info("Generated JSONs from playlist links.")

    def upload_to_mongodb(self):
        self.playlist_manager.upload_jsons_to_mongodb()
        self.logger.info("Uploaded JSONs to MongoDB.")

    def download_from_mongodb(self):
        self.playlist_manager.download_jsons_from_mongodb()
        self.logger.info("Downloaded JSONs from MongoDB.")

    def upload_to_youtube_music(self):
        self.playlist_manager.upload_to_youtube_music()
        self.logger.info("Uploaded playlists to YouTube Music.")

    def toggle_debug(self):
        self.logger.set_debug_mode(not self.logger.debug_mode)
        self.logger.info(f"Debug mode set to {self.logger.debug_mode}")
