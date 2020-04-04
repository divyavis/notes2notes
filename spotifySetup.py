import sys
import spotipy
import spotipy.util as util

class SpotifySetup(object):
    def __init__(self, username):
        self.username = username
    
    def getAuth(self):
        scope = "user-library-read" #read access to user's "Your Music" library
        clientId = "7b770ecc73434facafdfe5dccace0566"
        clientSecret = "347dff87da6c45ca95cdc71f6c935ceb"
        redirect = "https://sites.google.com/andrew.cmu.edu/authorizationredirect"
        token = util.prompt_for_user_token(self.username, scope,
                                            client_id=clientId,
                                            client_secret=clientSecret,
                                            redirect_uri=redirect)
        if token:
            self.sp = spotipy.Spotify(auth=token)
            self.savedTracks = self.sp.current_user_saved_tracks()
            
            
