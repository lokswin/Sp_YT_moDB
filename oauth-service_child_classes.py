from oauth_service_base_class import OAuthService

class YouTubeMusicOAuth(OAuthService):
    def __init__(self, client_id, client_secret, authorization_base_url, token_url, redirect_uri):
        super().__init__(client_id, client_secret, authorization_base_url, token_url, 'youtube', redirect_uri)
    
    def get_scope(self):
        return 'https://www.googleapis.com/auth/youtube.force-ssl'

class SpotifyOAuth(OAuthService):
    def __init__(self, client_id, client_secret, authorization_base_url, token_url, redirect_uri):
        super().__init__(client_id, client_secret, authorization_base_url, token_url, 'spotify', redirect_uri)
    
    def get_scope(self):
        return 'playlist-read-private playlist-modify-public playlist-modify-private'

class MongoOAuth(OAuthService):
    def __init__(self, client_id, client_secret, authorization_base_url, token_url, redirect_uri):
        super().__init__(client_id, client_secret, authorization_base_url, token_url, 'mongo', redirect_uri)
    
    def get_scope(self):
        return 'mongodb'
