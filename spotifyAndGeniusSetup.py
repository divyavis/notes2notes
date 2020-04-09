import module_manager
module_manager.review()
import os
import spotipy
import spotipy.util as util
import lyricsgenius
import requests
from bs4 import BeautifulSoup

class MusicSetup(object):
    def __init__(self, username):
        self.spotifyUsername = username
        self.songs = set()
        self.publicPlaylist = True

    #modified from https://spotipy.readthedocs.io/en/2.9.0/#module-spotipy.client
    def getSpotifyAuth(self):
        #if os.path.exists(f".cache-{self.spotifyUsername}"):
            #os.remove(f".cache-{self.spotifyUsername}")
        scope = "user-library-read, playlist-modify-public, playlist-modify-private, user-read-playback-state, streaming"
        clientId = "7b770ecc73434facafdfe5dccace0566"
        clientSecret = "347dff87da6c45ca95cdc71f6c935ceb"
        redirect = 'https://sites.google.com/andrew.cmu.edu/authorizationredirect'
        token = util.prompt_for_user_token(self.spotifyUsername, scope=scope,
                                            client_id=clientId,
                                            client_secret=clientSecret,
                                            redirect_uri=redirect)
        if token:
            self.sp = spotipy.Spotify(auth=token)
            self.savedTracks = self.sp.current_user_saved_tracks() #list of tracks saved in user’s “Your Music” library
            self.playlists = self.sp.user_playlists(self.spotifyUsername)
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
        return self.songs

    def addTracks(self, tracks):
        for item in tracks['items']:
            if len(self.songs) > 1000:
                break
            track = item['track']
            if self.isVocalTrack(track['id']):
                trackList = []
                trackList.append(track['name'])
                trackList.append(track['uri'])
                for i in range(len(track['artists'])):
                    trackList.append(track['artists'][i]['name'])
                trackTup = tuple(trackList)
                self.songs.add(trackTup)
    
    def getLyricsWithGenius(self, title, artist):
        clientToken = "ouarcaeWjKfIm5LhAydon-2Ii_isvB8g_-P2Z6bpyjJw7D5IMdCk9gP92l5aDs0C"
        genius = lyricsgenius.Genius(clientToken)
        song = genius.search_song(title, artist)
        if song != None:
            return song.lyrics
        return None

    def formatLink(self, word):
        word = word.lower()
        updatedWord = ""
        for letter in word:
            if letter.isalnum():
                updatedWord += letter
            elif letter == "'":
                continue
            else:
                updatedWord += "-"
        return updatedWord

    #modified from https://www.promptcloud.com/blog/scraping-song-lyrics-using-python-from-genius/
    def getLyricsV2(self, title, artist):
        title = self.formatLink(title)
        artist = self.formatLink(artist)
        URL = f"https://genius.com/{artist}-{title}-lyrics"
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        for div in soup.findAll('div', attrs = {'class': 'lyrics'}):
            lyricList = div.text.strip().split("\n")
        lyrics = ""
        for line in lyricList:
            lyrics += "\n" + line
        lyrics.strip()
        return lyrics

    def isVocalTrack(self, trackID):
        audioAnalysis = self.sp.audio_features(trackID)
        for elem in audioAnalysis:
            if elem['instrumentalness'] < 0.1:
                return True
        return False
    
    def createPlaylist(self):
        self.sp.user_playlist_create(self.spotifyUsername, name="april 6 playlist", public=self.publicPlaylist, description="keywords")
    
    def getDeviceID(self):
        deviceInfo = self.sp.devices()['devices']
        for elem in deviceInfo:
            if elem['type'] == 'Computer':
                return elem['id']
        return None

    def playSongs(self):
        deviceID = self.getDeviceID()
        if deviceID != None:
            self.sp.start_playback(device_id=deviceID, uris=[])
        else:
            return "cannot find your spotify device (must be desktop app)"
    
    def getTitleMatchedSongs(self, relevantWords):
        songList = []
        for song in self.songs:
            title = song[0]
            for word in relevantWords:
                if word in title:
                    songList.append(song)
        return songList
    
    def getSongLyrics(self, songList):
        lyricDict = dict()
        others = []
        for song in songList:
            title = song[0]
            artist = song[2]
            try:
                lyrics = self.getLyricsV2(title, artist)
            except:
                lyrics = None
            if lyrics != None:
                lyricDict[(title, song[1])] = lyrics
            else:
                others.append(song)
        for song in others:
            title = song[0]
            artist = song[2]
            lyrics = self.getLyricsWithGenius(title, artist)
            if lyrics != None:
                lyricDict[(title, song[1])] = lyrics
        return lyricDict


def countWordOccurrencesInSong(lyricsDict, relevantWords):
    pass

def runSpotify():
    divMusic = MusicSetup("divviswa")
    divMusic.getSpotifyAuth()
    #divMusic.makeSongSet()
    #divMusic.getLyrics("Bad to you", "Ariana Grande")
    print(divMusic.getLyricsWithGenius("Satellite Lovers", "Nenashi"))
    print("-----------------------------------------------------")
    print(divMusic.getLyricsV2("Satellite Lovers", "Nenashi"))
    #songList = divMusic.getTitleMatchedSongs(["today", "good", "day", "hung", "out", "friends", "ate", "dinner", "together"])
    #print(songList)
    #print(divMusic.getSongLyrics(songList))



runSpotify()
