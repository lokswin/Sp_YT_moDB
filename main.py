import json
from gui_class import GUI
from logger_class import Logger
from playlist_manager_class import PlaylistManager

def main():
    with open('config.json', 'r') as file:
        config = json.load(file)

    logger = Logger(config)
    playlist_manager = PlaylistManager(config)

    # Authenticate services
    playlist_manager.authenticate_spotify()
    playlist_manager.authenticate_mongo()
    playlist_manager.upload_to_youtube_music()

    gui = GUI(playlist_manager, logger)
    gui.run()

if __name__ == "__main__":
    main()
