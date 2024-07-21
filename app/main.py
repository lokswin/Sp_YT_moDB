import json, os
from app.logger_class import Logger
from app.playlist_manager_class import PlaylistManager

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
    playlist_manager = PlaylistManager(config)

    # Example usage
    playlist_links = playlist_manager.read_playlist_links()
    for link in playlist_links:
        playlist_manager.generate_json_from_playlist(link)
    playlist_manager.upload_to_youtube_music()

if __name__ == "__main__":
    main()
