import module_manager
module_manager.review()
import os
import spotipy
import spotipy.util as util
import lyricsgenius
import requests
from bs4 import BeautifulSoup

class MusicSetup(object):
    def __init__(self, username, month, day):
        self.spotifyUsername = username
        self.songs = set()
        self.publicPlaylist = True

    #modified from https://spotipy.readthedocs.io/en/2.9.0/#module-spotipy.client
    def getSpotifyAuth(self):
        if os.path.exists(f".cache-{self.spotifyUsername}"):
            os.remove(f".cache-{self.spotifyUsername}")
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

    def createPlaylist(self, trackIDs, descrip=None, month, day):
        if descrip != None:
            playlistDescrip = f"keywords: {descrip}"
        else:
            playlistDescrip = descrip
        self.sp.user_playlist_create(self.spotifyUsername, name=f"{month} {day} playlist", public=self.publicPlaylist, description=playlistDescrip)
        for item in self.sp.user_playlists(self.spotifyUsername)['items']:
            if item['name'] == f"{month} {day} playlist":
                playlistID = item['id']
                self.sp.user_playlist_add_tracks(self.spotifyUsername, playlist_id=playlistID, tracks=trackIDs)

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
            title = song[0]
            artist = song[2]
            try:
                lyrics = self.getLyricsV2(title, artist)
            except:
                lyrics = None
            if lyrics != None:
                lyricDict[(title, song[1])] = lyrics
        return lyricDict

    def getPlaylistTrackIDs(self, songList):
        trackIDs = []
        for song in songList:
            url = song[1]
            trackIDs.append(url)
        return trackIDs

journal = "Today, I had a good day. I hung out with my friends, and we ate dinner together."
nonWords = ["for", "and", "nor", "but", "or", "yet", "so"]

def getRelevantWords(journal, nonWords):
    journal = journal.lower()
    relevantWords = []
    for word in journal.split():
        cleanWord = ""
        for letter in word:
            if letter.isalnum():
                cleanWord += letter
        if cleanWord not in nonWords and len(cleanWord) >= 3:
            relevantWords.append(cleanWord)
    return relevantWords

def countWordOccurrencesInSong(lyricsDict, relevantWords):
    wordOccurrences = dict()
    for song in lyricsDict:
        wordOccurrences[song] = dict()
        wordCounts = wordOccurrences[song]
        for word in relevantWords:
            count = 0
            lyrics = lyricsDict[song]
            for lyric in lyrics.split():
                if lyric == word:
                    count += 1
            wordCounts[word] = count
        wordOccurrences[song] = wordCounts
    return wordOccurrences

def getKeywordsUsed(wordCountsDict):
    keywords = []
    for song in wordCountsDict:
        wordCounts = wordCountsDict[song]
        for word in wordCounts:
            if word not in keywords:
                keywords.append(word)
    return keywords

def scoreSongs(wordCountsDict):
    songScores = []
    for song in wordCountsDict:
        totalScore = 0
        title = song[0]
        url = song[1]
        wordCounts = wordCountsDict[song]
        for word in wordCounts:
            totalScore += wordCounts[word]
        songScores.append((title, url, totalScore))
    return songScores

#modified from https://www.cs.cmu.edu/~112/notes/notes-recursion-part1.html#mergesort
def merge(A, B):
    C = [ ]
    i = j = 0
    while ((i < len(A)) or (j < len(B))):
        if ((j == len(B)) or ((i < len(A)) and (A[i][2] >= B[j][2]))):
            C.append(A[i])
            i += 1
        else:
            C.append(B[j])
            j += 1
    return C

#uses common mergeSort function
def rankSongs(songScores):
    if len(songScores) < 2:
        return songScores
    else:
        mid = len(songScores)//2
        left = rankSongs(songScores[:mid])
        right = rankSongs(songScores[mid:])
        return merge(left, right)

def eliminateNonMatches(rankedSongs):
    updatedSongs = []
    for song in rankedSongs:
        if song[2] > 0:
            updatedSongs.append(song)
    return updatedSongs

def runSpotify():
    divMusic = MusicSetup("divviswa")
    divMusic.getSpotifyAuth()
    relevantWords = getRelevantWords(journal, nonWords)
    divMusic.makeSongSet()
    songList = divMusic.getTitleMatchedSongs(relevantWords)
    lyricsDict = divMusic.getSongLyrics(songList)
    wordCounts = countWordOccurrencesInSong(lyricsDict, relevantWords)
    keywords = getKeywordsUsed(wordCounts)
    keywordString = ", ".join(keywords)
    songScores = scoreSongs(wordCounts)
    rankedSongs = rankSongs(songScores)
    rankedSongs = eliminateNonMatches(rankedSongs)
    trackIDs = divMusic.getPlaylistTrackIDs(rankedSongs)
    divMusic.createPlaylist(trackIDs, descrip=keywordString, "april", "11")

runSpotify()
