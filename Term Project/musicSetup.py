import os
import spotipy
import spotipy.util as util
import lyricsgenius
import requests
from bs4 import BeautifulSoup

class MusicSetup(object):
    def __init__(self, username):
        self.spotifyUsername = username
        self.getSpotifyAuth()
        self.songs = set()
        self.publicPlaylist = True
        self.flash = False

    #modified from https://spotipy.readthedocs.io/en/2.9.0/#module-spotipy.client
    def getSpotifyAuth(self):
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
            self.gotAuth = True
        else:
            self.gotAuth = False

    #modified from https://spotipy.readthedocs.io/en/2.9.0/#module-spotipy.client
    def makeSongSet(self):
        for playlist in self.playlists['items']:
            if playlist['owner']['id'] == self.spotifyUsername:
                results = self.sp.user_playlist(self.spotifyUsername, playlist['id'], fields="tracks,next")
                tracks = results['tracks']
                self.addTracks(tracks)
        self.addTracks(self.savedTracks)
        return self.songs

    def formatTitle(self, title):
        title = title.lower()
        eliminations = [' (feat. ', ' [feat. ', ' feat. ', ' (with ', ' - from ', ' (from ', ' - remastered', ' - radio edit', ' - bonus track', ' (bonus track)', ' - edit', ' - single version', ' - radio version', ' - full length version', ' - live']
        updatedName = ""
        for word in eliminations:
            if word in title:
                wordIndex = title.find(word)
                updatedName += title[:wordIndex]
                return updatedName
        return title

    def addTracks(self, tracks):
        for item in tracks['items']:
            if len(self.songs) > 1000:
                break
            track = item['track']
            if self.isVocalTrack(track['id']):
                trackList = []
                trackList.append(track['name'].lower())
                trackList.append(track['uri'])
                for i in range(len(track['artists'])):
                    trackList.append((track['artists'][i]['name']).lower())
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
            elif letter == "&":
                updatedWord += 'and'
            elif letter == "'" or letter == '"' or letter == ".":
                continue
            elif updatedWord.endswith("-"):
                continue
            else:
                updatedWord += "-"
        return updatedWord

    #modified from https://www.promptcloud.com/blog/scraping-song-lyrics-using-python-from-genius/
    def getLyricsV2(self, song):
        title = song[0]
        if len(song) > 3:
            if ' (feat. ' in title or ' [feat. ' in title or ' feat. ' in title or len(song) > 5:
                title = self.formatTitle(title)
                title = self.formatLink(title)
                artist = song[2]
                artist = self.formatLink(artist)
                URL = f"https://genius.com/{artist}-{title}-lyrics"
                page = requests.get(URL)
                if page.status_code == 404:
                    return None
            elif len(song) == 4:
                title = self.formatTitle(title)
                title = self.formatLink(title)
                artist1 = song[2]
                artist2 = song[3]
                artist1 = self.formatLink(artist1)
                artist2 = self.formatLink(artist2)
                URL = f"https://genius.com/{artist1}-and-{artist2}-{title}-lyrics"
                page = requests.get(URL)
                if page.status_code == 404:
                    URL = f"https://genius.com/{artist1}-{title}-lyrics"
                    page = requests.get(URL)
                    if page.status_code == 404:
                        return None
            elif len(song) == 5:
                title = self.formatTitle(title)
                title = self.formatLink(title)
                artist1 = song[2]
                artist2 = song[3]
                artist3 = song[4]
                artist1 = self.formatLink(artist1)
                artist2 = self.formatLink(artist2)
                artist3 = self.formatLink(artist3)
                URL = f"https://genius.com/{artist1}-{artist2}-and-{artist3}-{title}-lyrics"
                page = requests.get(URL)
                if page.status_code == 404:
                    URL = f"https://genius.com/{artist1}-{title}-lyrics"
                    page = requests.get(URL)
                    if page.status_code == 404:
                        return None
            else:
                return None
        else:
            title = self.formatTitle(title)
            title = self.formatLink(title)
            artist = song[2]
            artist = self.formatLink(artist)
            URL = f"https://genius.com/{artist}-{title}-lyrics"
            page = requests.get(URL)
            if page.status_code == 404:
                return None
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

    def createPlaylist(self, trackIDs, month, day=None, publicP=True, descrip=None):
        if day != None:
            playlistName = f"{month} {day} playlist"
        else:
            playlistName = f"{month} playlist"
        self.sp.user_playlist_create(self.spotifyUsername, name=playlistName, public=True, description=descrip)
        for item in self.sp.user_playlists(self.spotifyUsername)['items']:
            if item['name'] == playlistName:
                playlistID = item['id']
                self.sp.user_playlist_add_tracks(self.spotifyUsername, playlist_id=playlistID, tracks=trackIDs)
        if publicP == False:
            self.sp.user_playlist_change_details(self.spotifyUsername, playlistID, public=False)

    def getDeviceID(self):
        deviceInfo = self.sp.devices()['devices']
        for elem in deviceInfo:
            if elem['type'] == 'Computer':
                return elem['id']
        return None

    def playSongs(self, trackIDs):
        deviceID = self.getDeviceID()
        if deviceID != None:
            self.sp.start_playback(device_id=deviceID, uris=trackIDs)
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
            lyrics = self.getLyricsV2(song)
            if lyrics != None:
                lyricDict[(song[0], song[1])] = lyrics
        return lyricDict

    def getPlaylistTrackIDs(self, songList):
        trackIDs = []
        for song in songList:
            url = song[1]
            trackIDs.append(url)
        return trackIDs
