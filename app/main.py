# file: app/main.py
import json
import os
from app.logger_class import Logger
from app.playlist_manager_class import PlaylistManager
from app.gui_class import AppGUI
import tkinter as tk

def load_config():
    """
    Loads the configuration from a JSON file.

    Returns:
        dict: The configuration settings from the JSON file.
    """
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    return config

def main():
    """
    The main function to start the application, initialize the API clients, and handle
    application logic based on the configuration file.
    """
    # Load configuration
    config = load_config()
    logger = Logger(debug_mode=config.get("debug_mode", False))
    
    # Initialize Playlist Manager
    playlist_manager = PlaylistManager(config, logger)

    # Start the GUI
    root = tk.Tk()
    app = AppGUI(root, playlist_manager, logger)
    root.mainloop()

if __name__ == "__main__":
    main()
