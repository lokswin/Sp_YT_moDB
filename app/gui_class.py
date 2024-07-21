# file: app/gui_class.py
import tkinter as tk
from tkinter import ttk, Menu
from app.playlist_manager_class import PlaylistManager
from app.logger_class import Logger

class AppGUI:
    def __init__(self, root, playlist_manager, logger):
        self.root = root
        self.root.title("Authorization Manager")
        self.playlist_manager = playlist_manager
        self.logger = logger
        self.buttons = []
        self.status_labels = {}
        self.create_widgets()
        self.logger.set_gui_log_widget(self.log_text)
        self.auto_check_authorizations()

    def create_widgets(self):
        self.create_menu()
        self.create_button_area()
        self.create_status_area()
        self.create_log_area()

    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)

        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About")

    def create_button_area(self):
        button_frame = ttk.LabelFrame(self.root, text="Controls", padding="10")
        button_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

        self.create_button(button_frame, "Check Authorization YT", self.check_authorization_yt, 0)
        self.create_button(button_frame, "Check Authorization Google", self.check_authorization_google, 1)
        self.create_button(button_frame, "Check Authorization MongoDB", self.check_authorization_mongo, 2)
        self.create_button(button_frame, "Logout YT", self.logout_yt, 3)
        self.create_button(button_frame, "Logout Google", self.logout_google, 4)
        self.create_button(button_frame, "Logout MongoDB", self.logout_mongo, 5)
        self.create_button(button_frame, "Login YT", self.login_yt, 6)
        self.create_button(button_frame, "Login Google", self.login_google, 7)
        self.create_button(button_frame, "Login MongoDB", self.login_mongo, 8)

    def create_status_area(self):
        status_frame = ttk.LabelFrame(self.root, text="Service Status", padding="10")
        status_frame.grid(row=0, column=1, padx=10, pady=10, sticky=(tk.N, tk.S, tk.E))

        self.status_labels = {
            "yt": self.create_status_label(status_frame, "YouTube", 0),
            "google": self.create_status_label(status_frame, "Google", 1),
            "mongo": self.create_status_label(status_frame, "MongoDB", 2),
        }

    def create_log_area(self):
        log_frame = ttk.LabelFrame(self.root, text="Log", padding="10")
        log_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, state='disabled')
        self.log_text.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

    def create_button(self, frame, text, command, row):
        button = ttk.Button(frame, text=text, command=command)
        button.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        self.buttons.append(button)

    def create_status_label(self, frame, text, row):
        label = ttk.Label(frame, text=f"{text}: N/A", foreground="gray")
        label.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        return label

    def set_status(self, service, status):
        if status == "authorized":
            self.status_labels[service].config(text=f"{service.capitalize()}: Authorized", foreground="green")
        else:
            self.status_labels[service].config(text=f"{service.capitalize()}: N/A", foreground="gray")

    def hide_buttons(self):
        for button in self.buttons:
            button.grid_remove()

    def show_buttons(self):
        for button in self.buttons:
            button.grid()

    def auto_check_authorizations(self):
        self.hide_buttons()
        self.root.after(100, self.check_all_authorizations)

    def check_all_authorizations(self):
        self.check_authorization_yt()
        self.check_authorization_google()
        self.check_authorization_mongo()
        self.show_buttons()

    def check_authorization_yt(self):
        self.logger.info("Checking YouTube authorization...")
        if self.playlist_manager.is_authorized('youtube_music'):
            self.set_status("yt", "authorized")
            self.logger.info("YouTube authorization successful.")
        else:
            self.set_status("yt", "unauthorized")
            self.logger.info("YouTube authorization failed.")

    def check_authorization_google(self):
        self.logger.info("Checking Spotify authorization...")
        if self.playlist_manager.is_authorized('spotify'):
            self.set_status("google", "authorized")
            self.logger.info("Spotify authorization successful.")
        else:
            self.set_status("google", "unauthorized")
            self.logger.info("Spotify authorization failed.")

    def check_authorization_mongo(self):
        self.logger.info("Checking MongoDB authorization...")
        if self.playlist_manager.is_authorized('mongo'):
            self.set_status("mongo", "authorized")
            self.logger.info("MongoDB authorization successful.")
        else:
            self.set_status("mongo", "unauthorized")
            self.logger.info("MongoDB authorization failed.")

    def logout_yt(self):
        self.logger.info("Logging out from YouTube...")
        self.playlist_manager.logout('youtube_music')
        self.set_status("yt", "unauthorized")
        self.logger.info("Logged out from YouTube.")

    def logout_google(self):
        self.logger.info("Logging out from Spotify...")
        self.playlist_manager.logout('spotify')
        self.set_status("google", "unauthorized")
        self.logger.info("Logged out from Spotify.")

    def logout_mongo(self):
        self.logger.info("Logging out from MongoDB...")
        self.playlist_manager.logout('mongo')
        self.set_status("mongo", "unauthorized")
        self.logger.info("Logged out from MongoDB.")

    def login_yt(self):
        self.logger.info("Logging in to YouTube...")
        self.playlist_manager.authenticate('youtube_music')
        self.check_authorization_yt()

    def login_google(self):
        self.logger.info("Logging in to Spotify...")
        self.playlist_manager.authenticate('spotify')
        self.check_authorization_google()

    def login_mongo(self):
        self.logger.info("Logging in to MongoDB...")
        self.playlist_manager.authenticate('mongo')
        self.check_authorization_mongo()

def main():
    from app.main import load_config
    config = load_config()
    logger = Logger(debug_mode=config.get("debug_mode", False))
    playlist_manager = PlaylistManager(config, logger)
    
    root = tk.Tk()
    app = AppGUI(root, playlist_manager, logger)
    root.mainloop()

if __name__ == "__main__":
    main()
