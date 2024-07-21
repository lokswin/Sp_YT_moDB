from .oauth_service_base_class import OAuthService

class YouTubeMusicOAuth(OAuthService):
    def get_scope(self):
        return 'https://www.googleapis.com/auth/youtube.force-ssl'

class SpotifyOAuth(OAuthService):
    def get_scope(self):
        return 'playlist-read-private playlist-modify-private playlist-modify-public'

class MongoOAuth(OAuthService):
    def get_scope(self):
        return ''  # MongoDB may not use scopes, adjust as necessary
