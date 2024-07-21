# file: app/gui_class.py
import tkinter as tk
from tkinter import ttk
from app.oauth_service_child_classes import YouTubeMusicOAuth, SpotifyOAuth, MongoOAuth
from app.playlist_manager_class import PlaylistManager

class AppGUI:
    def __init__(self, root, playlist_manager):
        self.root = root
        self.root.title("Authorization Manager")
        self.playlist_manager = playlist_manager
        self.create_widgets()

    def create_widgets(self):
        # Create a frame for the buttons and status indicators
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create buttons and status labels
        self.create_button(frame, "Check Authorization YT", self.check_authorization_yt, 0)
        self.create_button(frame, "Check Authorization Google", self.check_authorization_google, 1)
        self.create_button(frame, "Check Authorization MongoDB", self.check_authorization_mongo, 2)
        self.create_button(frame, "Logout YT", self.logout_yt, 3)
        self.create_button(frame, "Logout Google", self.logout_google, 4)
        self.create_button(frame, "Logout MongoDB", self.logout_mongo, 5)
        self.create_button(frame, "Login YT", self.login_yt, 6)
        self.create_button(frame, "Login Google", self.login_google, 7)
        self.create_button(frame, "Login MongoDB", self.login_mongo, 8)

        self.status_labels = {
            "yt": self.create_status_label(frame, "YouTube"),
            "google": self.create_status_label(frame, "Google"),
            "mongo": self.create_status_label(frame, "MongoDB"),
        }

    def create_button(self, frame, text, command, row):
        button = ttk.Button(frame, text=text, command=command)
        button.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)

    def create_status_label(self, frame, text):
        label = ttk.Label(frame, text=f"{text}: N/A", foreground="gray")
        label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        return label

    def set_status(self, service, status):
        if status == "authorized":
            self.status_labels[service].config(text=f"{service.capitalize()}: Authorized", foreground="green")
        else:
            self.status_labels[service].config(text=f"{service.capitalize()}: N/A", foreground="gray")

    def check_authorization_yt(self):
        if self.playlist_manager.is_authorized('youtube_music'):
            self.set_status("yt", "authorized")
        else:
            self.set_status("yt", "unauthorized")

    def check_authorization_google(self):
        if self.playlist_manager.is_authorized('spotify'):
            self.set_status("google", "authorized")
        else:
            self.set_status("google", "unauthorized")

    def check_authorization_mongo(self):
        if self.playlist_manager.is_authorized('mongo'):
            self.set_status("mongo", "authorized")
        else:
            self.set_status("mongo", "unauthorized")

    def logout_yt(self):
        self.playlist_manager.logout('youtube_music')
        self.set_status("yt", "unauthorized")

    def logout_google(self):
        self.playlist_manager.logout('spotify')
        self.set_status("google", "unauthorized")

    def logout_mongo(self):
        self.playlist_manager.logout('mongo')
        self.set_status("mongo", "unauthorized")

    def login_yt(self):
        self.playlist_manager.authenticate('youtube_music')
        self.check_authorization_yt()

    def login_google(self):
        self.playlist_manager.authenticate('spotify')
        self.check_authorization_google()

    def login_mongo(self):
        self.playlist_manager.authenticate('mongo')
        self.check_authorization_mongo()

def main():
    from app.main import load_config
    config = load_config()
    playlist_manager = PlaylistManager(config)
    
    root = tk.Tk()
    app = AppGUI(root, playlist_manager)
    root.mainloop()

if __name__ == "__main__":
    main()
