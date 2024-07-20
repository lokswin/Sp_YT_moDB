import json
from gui_class import GUI
from logger_class import Logger
from playlist_manager_class import PlaylistManager

# Load configuration
with open('config.json', 'r') as file:
    config = json.load(file)

# Initialize Logger
logger = Logger(debug_mode=config.get('debug_mode', False))

# Initialize Playlist Manager
playlist_manager = PlaylistManager(config)

# Initialize and start GUI
gui = GUI(playlist_manager, logger)
