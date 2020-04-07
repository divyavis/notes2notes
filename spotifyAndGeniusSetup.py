import os
import spotipy
import spotipy.util as util
import lyricsgenius

class MusicSetup(object):
    def __init__(self, username):
        self.spotifyUsername = username
        self.songs = set()

    #modified from https://spotipy.readthedocs.io/en/2.9.0/#module-spotipy.client
    def getSpotifyAuth(self):
        #if os.path.exists(f".cache-{self.spotifyUsername}"):
            #os.remove(f".cache-{self.spotifyUsername}")
        scope = "user-library-read" #read access to user's "Your Music" library
        clientId = "7b770ecc73434facafdfe5dccace0566"
        clientSecret = "347dff87da6c45ca95cdc71f6c935ceb"
        redirect = 'https://sites.google.com/andrew.cmu.edu/authorizationredirect'
        token = util.prompt_for_user_token(self.spotifyUsername, scope,
                                            client_id=clientId,
                                            client_secret=clientSecret,
                                            redirect_uri=redirect)
        if token:
            self.sp = spotipy.Spotify(auth=token)
            self.savedTracks = self.sp.current_user_saved_tracks() #list of tracks saved in user’s “Your Music” library
            self.playlists = self.sp.user_playlists(self.spotifyUsername)
            """for playlist in playlists['items']:
                if playlist['owner']['id'] == self.spotifyUsername:
                    print()
                    print(playlist['name'])
                    print ('  total tracks', playlist['tracks']['total'])
                    results = self.sp.playlist(playlist['id'],
                        fields="tracks,next")
                    tracks = results['tracks']
                    self.show_tracks(tracks)
                    while tracks['next']:
                        tracks = self.sp.next(tracks)
                        self.show_tracks(tracks)          
            for item in self.savedTracks['items']:
                track = item['track']
                print(track)
                print((track['name']) + ' - ' + track['artists'][0]['name']))"""
        else:
            print("Can't get token for", self.spotifyUsername)
    
    #modified from https://spotipy.readthedocs.io/en/2.9.0/#module-spotipy.client
    def makeSongSet(self):
        for playlist in self.playlists['items']:
            if playlist['owner']['id'] == self.spotifyUsername:
                results = self.sp.user_playlist(self.spotifyUsername, playlist['id'], fields="tracks,next")
                tracks = results['tracks']
                self.addTracks(tracks)
        self.addTracks(self.savedTracks)
        """for song in self.songs:
            title = song[0]
            artist = song[1]
            if self.getLyrics(title, artist) == None:
                self.songs.remove(song)
                    #if trackDict not in self.songInfo:
                        #self.songInfo.append(trackDict)"""
        print(len(self.songs))
        return self.songs

    def addTracks(self, tracks):
        for item in tracks['items']:
            if len(self.songs) > 1000:
                break
            track = item['track']
            if self.isVocalTrack(track['id']):
                trackList = []
                trackList.append(track['name'])
                for i in range(len(track['artists'])):
                    trackList.append(track['artists'][i]['name'])
                trackTup = tuple(trackList)
                self.songs.add(trackTup)

    def getTrackInfo(self, tracks):
        for item in tracks['items']:
            trackDict = dict()
            track = item['track']
            trackDict['song'] = track['name']
            trackDict['artists'] = []
            for i in range(len(track['artists'])):
                trackDict['artists'].append(track['artists'][i]['name'])
            self.songInfo.append(trackDict)

    def show_tracks(self, tracks):
        for i, item in enumerate(tracks['items']):
            track = item['track']
            print("   %d %32.32s %s" % (i, track['artists'][0]['name'],
                track['name']))
    
    def getLyrics(self, title, artist):
        clientToken = "ouarcaeWjKfIm5LhAydon-2Ii_isvB8g_-P2Z6bpyjJw7D5IMdCk9gP92l5aDs0C"
        genius = lyricsgenius.Genius(clientToken)
        song = genius.search_song(title, artist)
        print(song.lyrics)
        return song.lyrics

    def isVocalTrack(self, trackID):
        audioAnalysis = self.sp.audio_features(trackID)
        for elem in audioAnalysis:
            if elem['instrumentalness'] < 0.1:
                return True
        return False

def runSpotify():
    divMusic = MusicSetup("divviswa")
    divMusic.getSpotifyAuth()
    #print(divMusic.makeSongSet())
    #divMusic.getLyrics("Bad to you", "Ariana Grande")

runSpotify()
