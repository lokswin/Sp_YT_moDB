import pymongo

class YouTubeMusicOAuth(OAuthService):
    def __init__(self, client_id, client_secret):
        super().__init__(client_id, client_secret,
                         'https://accounts.google.com/o/oauth2/v2/auth',
                         'https://oauth2.googleapis.com/token',
                         'youtube')

class SpotifyOAuth(OAuthService):
    def __init__(self, client_id, client_secret):
        super().__init__(client_id, client_secret,
                         'https://accounts.spotify.com/authorize',
                         'https://accounts.spotify.com/api/token',
                         'spotify')

class MongoDBAuth:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def connect(self):
        client = pymongo.MongoClient(f"mongodb+srv://{self.username}:{self.password}@cluster0.mongodb.net/test?retryWrites=true&w=majority")
        db = client.test
        return db
